"""
Views for User management.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, UserUpdateSerializer,
    StaffCreateSerializer, AdminCreateSerializer, UserListSerializer
)
from subscriptions.models import Subscription
from meals.models import MealOrder
from payments.models import Transaction


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'cps_number': user.cps_number,
            'daily_code': user.daily_code,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Ensure daily code is current
        user.get_current_code()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """User logout endpoint."""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'message': 'Successfully logged out'})


class MeView(generics.RetrieveUpdateAPIView):
    """Get/Update current user profile."""
    serializer_class = UserSerializer
    
    def get_object(self):
        # Ensure daily code is current
        user = self.request.user
        user.get_current_code()
        return user
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """Change user password."""
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'detail': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})


class TokenRefreshView(APIView):
    """Refresh JWT token."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access': str(refresh.access_token)})
        except Exception:
            return Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


# Permission Classes
class IsAdminOrAbove(permissions.BasePermission):
    """Permission for admin users and above."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'super_admin', 'developer']


class IsAdminUser(permissions.BasePermission):
    """Permission for admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'super_admin', 'developer']


class IsSuperAdmin(permissions.BasePermission):
    """Permission for super admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'developer']


class IsStaff(permissions.BasePermission):
    """Permission for staff users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['staff', 'admin', 'super_admin', 'developer']


# Admin Views
class AdminDashboardView(APIView):
    """Admin dashboard statistics."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        user = request.user
        restaurant_filter = {}
        if user.role == 'admin' and user.restaurant:
            restaurant_filter = {'restaurant': user.restaurant}
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Get statistics - changed from 'student' to 'user'
        total_users = User.objects.filter(role='user', **restaurant_filter).count()
        active_subscriptions = Subscription.objects.filter(
            status='active',
            user__restaurant=user.restaurant if user.role == 'admin' else None
        ).count() if user.restaurant or user.role != 'admin' else 0
        
        todays_orders = MealOrder.objects.filter(
            order_date=today,
            meal__restaurant=user.restaurant if user.role == 'admin' else None
        ).count() if user.restaurant or user.role != 'admin' else 0
        
        revenue_this_month = Transaction.objects.filter(
            status='completed',
            created_at__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'total_users': total_users,
            'active_subscriptions': active_subscriptions,
            'todays_orders': todays_orders,
            'revenue_this_month': revenue_this_month,
        })


class AdminUserListView(generics.ListAPIView):
    """List all users for admin (previously AdminStudentListView)."""
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(role='user')
        
        if user.role == 'admin' and user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(cps_number__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(daily_code__icontains=search)
            )
        
        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(is_active=(status_filter == 'active'))
        
        # Region filter
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(
                Q(region=region) | Q(restaurant__region=region)
            )
        
        return queryset


# Legacy alias for backwards compatibility
AdminStudentListView = AdminUserListView


class AdminStaffListView(generics.ListCreateAPIView):
    """List and create staff users."""
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StaffCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(role='staff')
        
        if user.role == 'admin' and user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            serializer.save(restaurant=user.restaurant)
        else:
            serializer.save()


class AdminStaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete staff user."""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(role='staff')
        
        if user.role == 'admin' and user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        return queryset


class DemandReportView(APIView):
    """Get meal demand report for admin."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        date = request.query_params.get('date', timezone.now().date())
        user = request.user
        
        orders = MealOrder.objects.filter(order_date=date)
        if user.role == 'admin' and user.restaurant:
            orders = orders.filter(meal__restaurant=user.restaurant)
        
        report = orders.values('meal__meal_type', 'meal__name').annotate(
            total_orders=Count('id'),
            served=Count('id', filter=Q(status='served')),
            pending=Count('id', filter=Q(status__in=['pending', 'confirmed']))
        )
        
        return Response([{
            'meal_type': r['meal__meal_type'],
            'meal_name': r['meal__name'],
            'total_orders': r['total_orders'],
            'served': r['served'],
            'pending': r['pending']
        } for r in report])


class RevenueReportView(APIView):
    """Get revenue report for admin."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = Transaction.objects.filter(status='completed')
        
        if start_date:
            transactions = transactions.filter(created_at__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__date__lte=end_date)
        
        total = transactions.aggregate(total=Sum('amount'))['total'] or 0
        by_method = transactions.values('payment_method').annotate(
            amount=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'total_revenue': total,
            'transactions_count': transactions.count(),
            'by_payment_method': [
                {'method': m['payment_method'], 'amount': m['amount'], 'count': m['count']}
                for m in by_method
            ]
        })


# Verify User Code (for staff)
class VerifyUserCodeView(APIView):
    """Verify a user's daily code (for staff at food service locations)."""
    permission_classes = [IsStaff]
    
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response(
                {'detail': 'Code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by daily code
        try:
            user = User.objects.get(daily_code=code, is_active=True)
            
            # Check if code is from today
            today = timezone.now().date()
            if user.daily_code_date != today:
                return Response({
                    'valid': False,
                    'message': 'Code has expired'
                })
            
            # Check for active subscription
            subscription = Subscription.objects.filter(
                user=user,
                status='active'
            ).first()
            
            return Response({
                'valid': True,
                'user': {
                    'id': str(user.id),
                    'full_name': user.full_name,
                    'cps_number': user.cps_number,
                    'restaurant_name': user.restaurant_name,
                },
                'subscription': {
                    'plan_name': subscription.plan.name if subscription else None,
                    'remaining_meals': subscription.remaining_meals if subscription else 0,
                    'expires_at': subscription.end_date if subscription else None,
                } if subscription else None
            })
        except User.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Invalid code'
            })


# Super Admin Views
class SuperAdminUserListView(generics.ListAPIView):
    """List all users for super admin."""
    serializer_class = UserListSerializer
    permission_classes = [IsSuperAdmin]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        restaurant_id = self.request.query_params.get('restaurant_id')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(
                Q(region=region) | Q(restaurant__region=region)
            )
        
        return queryset


class SuperAdminCreateAdminView(generics.CreateAPIView):
    """Create admin users (super admin only)."""
    serializer_class = AdminCreateSerializer
    permission_classes = [IsSuperAdmin]


class SuperAdminSystemStatsView(APIView):
    """Get system-wide statistics."""
    permission_classes = [IsSuperAdmin]
    
    def get(self, request):
        from restaurants.models import Restaurant
        
        return Response({
            'total_users': User.objects.count(),
            'total_regular_users': User.objects.filter(role='user').count(),
            'total_staff': User.objects.filter(role='staff').count(),
            'total_admins': User.objects.filter(role='admin').count(),
            'total_restaurants': Restaurant.objects.filter(is_active=True).count(),
            'active_subscriptions': Subscription.objects.filter(status='active').count(),
            'total_revenue': Transaction.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
        })


class SuperAdminResetPasswordView(APIView):
    """Reset a user's password (super admin only)."""
    permission_classes = [IsSuperAdmin]
    
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        new_password = request.data.get('new_password')
        if not new_password or len(new_password) < 6:
            return Response(
                {'detail': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': f'Password reset successfully for {user.full_name}',
            'user_id': str(user.id),
            'phone_number': user.phone_number
        })


class SuperAdminUpdateUserView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a user (super admin only)."""
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()
    
    def perform_destroy(self, instance):
        # Soft delete - just deactivate the user
        instance.is_active = False
        instance.save()


# User Dashboard
class UserDashboardView(APIView):
    """Get user dashboard stats (previously StudentDashboardView)."""
    
    def get(self, request):
        user = request.user
        
        # Ensure daily code is current
        user.get_current_code()
        
        # Get active subscription
        subscription = Subscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        # Get upcoming orders
        upcoming_orders = MealOrder.objects.filter(
            user=user,
            status__in=['pending', 'confirmed'],
            order_date__gte=timezone.now().date()
        ).select_related('meal')[:5]
        
        # Get recent orders
        recent_orders = MealOrder.objects.filter(
            user=user
        ).select_related('meal').order_by('-created_at')[:10]
        
        from meals.serializers import MealOrderSerializer
        from subscriptions.serializers import SubscriptionSerializer
        
        return Response({
            'daily_code': user.daily_code,
            'qr_code_data': user.qr_code_data,
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
            'remaining_meals': subscription.remaining_meals if subscription else 0,
            'upcoming_orders': MealOrderSerializer(upcoming_orders, many=True).data,
            'recent_orders': MealOrderSerializer(recent_orders, many=True).data,
        })


# Legacy alias for backwards compatibility
StudentDashboardView = UserDashboardView
