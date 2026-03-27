"""
Views for Meal management.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q

from .models import Meal, MealOrder
from .serializers import (
    MealSerializer, MealOrderSerializer,
    SelectMealSerializer, VerifyStudentSerializer, ServeMealSerializer
)
from users.views import IsAdminUser
from users.models import User
from subscriptions.models import Subscription


class MealListView(generics.ListAPIView):
    """List available meals."""
    serializer_class = MealSerializer
    
    def get_queryset(self):
        queryset = Meal.objects.filter(available_date__gte=timezone.now().date())
        
        # Filter by user's restaurant if logged in
        user = self.request.user
        if user.is_authenticated and user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(available_date=date)
        
        return queryset


class MealDetailView(generics.RetrieveAPIView):
    """Get meal details."""
    queryset = Meal.objects.all()
    serializer_class = MealSerializer


class SelectMealView(generics.CreateAPIView):
    """Select/order a meal."""
    serializer_class = SelectMealSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            MealOrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class MyOrdersView(generics.ListAPIView):
    """Get user's meal orders."""
    serializer_class = MealOrderSerializer
    
    def get_queryset(self):
        queryset = MealOrder.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.select_related('meal', 'subscription')


class OrderListView(generics.ListAPIView):
    """List all orders (admin/staff)."""
    serializer_class = MealOrderSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = MealOrder.objects.all()
        
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(order_date=date)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('user', 'meal')


class CancelOrderView(APIView):
    """Cancel a meal order."""
    
    def delete(self, request, pk):
        try:
            order = MealOrder.objects.get(id=pk, user=request.user)
            if order.status in ['pending', 'confirmed']:
                order.status = 'cancelled'
                order.save()
                
                # Restore meal count
                order.meal.current_orders -= 1
                order.meal.save()
                
                # Restore subscription meal
                order.subscription.remaining_meals += 1
                order.subscription.save()
                
                return Response({'message': 'Order cancelled'})
            return Response(
                {'detail': 'Cannot cancel this order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except MealOrder.DoesNotExist:
            return Response(
                {'detail': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# Admin Views
class AdminMealListView(generics.ListCreateAPIView):
    """List and create meals (admin only)."""
    serializer_class = MealSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Meal.objects.all()
        
        if user.role == 'admin' and user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(available_date=date)
        
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            serializer.save(restaurant=user.restaurant)
        else:
            serializer.save()


class AdminMealDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete meal (admin only)."""
    serializer_class = MealSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            return Meal.objects.filter(restaurant=user.restaurant)
        return Meal.objects.all()


# Staff Views
class IsStaffUser(permissions.BasePermission):
    """Permission for staff users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['staff', 'admin', 'super_admin', 'developer']


class StaffVerifyView(APIView):
    """
    Staff verification of user by CPS code or QR code.
    
    Time-locked verification:
    - Checks if current time is within valid meal window
    - Checks if user has already been served for this meal slot today
    - Validates active subscription
    """
    permission_classes = [IsStaffUser]
    
    # Meal windows (in minutes from midnight)
    MEAL_WINDOWS = {
        'tea': {'start': 360, 'end': 600, 'name': 'Morning Tea'},      # 6:00 AM - 10:00 AM
        'lunch': {'start': 690, 'end': 870, 'name': 'Lunch'},          # 11:30 AM - 2:30 PM
        'evening': {'start': 1020, 'end': 1200, 'name': 'Evening'},    # 5:00 PM - 8:00 PM
    }
    
    def get_current_meal_type(self):
        """Determine current meal type based on time of day."""
        now = timezone.localtime()
        current_minutes = now.hour * 60 + now.minute
        
        for meal_type, window in self.MEAL_WINDOWS.items():
            if window['start'] <= current_minutes <= window['end']:
                return meal_type
        return None
    
    def post(self, request):
        serializer = VerifyStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cps_code = serializer.validated_data.get('cps_number') or serializer.validated_data.get('qr_code')
        
        if not cps_code:
            return Response({
                'valid': False,
                'message': 'CPS code or QR code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        
        # 1. Check if current time is within a meal window
        current_meal = self.get_current_meal_type()
        if not current_meal:
            return Response({
                'valid': False,
                'message': 'No meal service at this time. Meal windows: Morning Tea (6-10 AM), Lunch (11:30-2:30 PM), Evening (5-8 PM)'
            })
        
        # 2. Find user by CPS code (permanent) or daily code
        try:
            # Try finding by permanent CPS number first
            user = User.objects.filter(cps_number=cps_code, is_active=True).first()
            
            # If not found, try daily code
            if not user:
                user = User.objects.filter(daily_code=cps_code, daily_code_date=today, is_active=True).first()
            
            if not user:
                return Response({
                    'valid': False,
                    'message': 'Invalid or expired code'
                })
        except User.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'User not found'
            })
        
        # 3. Check if user has already been served for this meal slot today
        already_served = MealOrder.objects.filter(
            user=user,
            meal_type=current_meal,
            order_date=today,
            status='served'
        ).exists()
        
        if already_served:
            meal_name = self.MEAL_WINDOWS[current_meal]['name']
            return Response({
                'valid': False,
                'message': f'{meal_name} already served today'
            })
        
        # 4. Check for active subscription
        subscription = Subscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        if not subscription:
            return Response({
                'valid': False,
                'user': {
                    'full_name': user.full_name,
                    'cps_number': user.cps_number,
                },
                'message': 'No active subscription'
            })
        
        # 5. Get or create today's order for this meal type
        todays_order = MealOrder.objects.filter(
            user=user,
            meal_type=current_meal,
            order_date=today
        ).first()
        
        from users.serializers import UserSerializer
        from subscriptions.serializers import SubscriptionSerializer
        
        return Response({
            'valid': True,
            'user': UserSerializer(user).data,
            'current_meal_type': current_meal,
            'meal_window': self.MEAL_WINDOWS[current_meal]['name'],
            'subscription': SubscriptionSerializer(subscription).data,
            'todays_order': MealOrderSerializer(todays_order).data if todays_order else None,
            'message': f'Ready to serve {self.MEAL_WINDOWS[current_meal]["name"]}'
        })


class StaffServeMealView(APIView):
    """
    Staff serve meal to user.
    
    Can either:
    1. Serve an existing order (by order_id)
    2. Create and serve a new order (by cps_code for the current meal window)
    """
    permission_classes = [IsStaffUser]
    
    MEAL_WINDOWS = {
        'tea': {'start': 360, 'end': 600},
        'lunch': {'start': 690, 'end': 870},
        'evening': {'start': 1020, 'end': 1200},
    }
    
    def get_current_meal_type(self):
        now = timezone.localtime()
        current_minutes = now.hour * 60 + now.minute
        for meal_type, window in self.MEAL_WINDOWS.items():
            if window['start'] <= current_minutes <= window['end']:
                return meal_type
        return None
    
    def post(self, request):
        order_id = request.data.get('order_id')
        cps_code = request.data.get('cps_code')
        
        today = timezone.now().date()
        current_meal = self.get_current_meal_type()
        
        if not current_meal:
            return Response({
                'error': 'No meal service at this time'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if order_id:
            # Serve existing order
            try:
                order = MealOrder.objects.get(id=order_id)
                order.mark_served(request.user)
                return Response(MealOrderSerializer(order).data)
            except MealOrder.DoesNotExist:
                return Response({
                    'error': 'Order not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        elif cps_code:
            # Find user and create/serve order
            user = User.objects.filter(cps_number=cps_code, is_active=True).first()
            if not user:
                user = User.objects.filter(daily_code=cps_code, daily_code_date=today, is_active=True).first()
            
            if not user:
                return Response({
                    'error': 'Invalid code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already served
            if MealOrder.has_been_served_today(user, current_meal):
                return Response({
                    'error': f'{current_meal.title()} already served today'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create order and mark as served
            order, created = MealOrder.objects.get_or_create(
                user=user,
                meal_type=current_meal,
                order_date=today,
                defaults={
                    'restaurant': user.restaurant,
                    'status': 'served',
                    'served_at': timezone.now(),
                    'served_by': request.user,
                }
            )
            
            if not created:
                order.mark_served(request.user)
            
            return Response({
                'success': True,
                'meal_type': current_meal,
                'user_name': user.full_name,
                'order': MealOrderSerializer(order).data
            })
        
        return Response({
            'error': 'Either order_id or cps_code is required'
        }, status=status.HTTP_400_BAD_REQUEST)


class StaffTodaysOrdersView(generics.ListAPIView):
    """Get today's orders for staff."""
    serializer_class = MealOrderSerializer
    permission_classes = [IsStaffUser]
    
    def get_queryset(self):
        today = timezone.now().date()
        user = self.request.user
        
        queryset = MealOrder.objects.filter(order_date=today)
        if user.restaurant:
            queryset = queryset.filter(restaurant=user.restaurant)
        
        return queryset.select_related('user', 'meal')


class StaffStatsView(APIView):
    """Get staff statistics."""
    permission_classes = [IsStaffUser]
    
    def get(self, request):
        today = timezone.now().date()
        user = request.user
        
        orders = MealOrder.objects.filter(order_date=today)
        if user.restaurant:
            orders = orders.filter(restaurant=user.restaurant)
        
        # Get stats for meals served by this staff member
        my_served = MealOrder.objects.filter(served_by=user, order_date=today).count()
        
        return Response({
            'served_today': orders.filter(status='served').count(),
            'pending_today': orders.filter(status__in=['pending', 'confirmed']).count(),
            'my_served_today': my_served,
        })


class StaffServiceHistoryView(generics.ListAPIView):
    """
    Get service history for the current staff member.
    Shows all users they have served with their subscription status.
    """
    serializer_class = MealOrderSerializer
    permission_classes = [IsStaffUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = MealOrder.objects.filter(served_by=user, status='served')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        date = self.request.query_params.get('date')
        
        if date:
            queryset = queryset.filter(order_date=date)
        else:
            if start_date:
                queryset = queryset.filter(order_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(order_date__lte=end_date)
        
        return queryset.select_related('user', 'meal').order_by('-served_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Get unique users served
        users_served = queryset.values('user').distinct().count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['users_served_count'] = users_served
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'users_served_count': users_served
        })


class StaffUserSubscriptionCheckView(APIView):
    """
    Check a user's subscription status when staff verifies them.
    Returns days left and whether user can be served.
    """
    permission_classes = [IsStaffUser]
    
    def get(self, request, user_id):
        """Check subscription status for a specific user."""
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        subscription = Subscription.objects.filter(
            user=target_user,
            status='active'
        ).select_related('plan', 'dietary_plan').first()
        
        if not subscription:
            return Response({
                'user_id': str(target_user.id),
                'user_name': target_user.full_name,
                'has_subscription': False,
                'can_serve': False,
                'message': 'No active subscription. User must pay to continue receiving meals.'
            })
        
        # Check if expired
        subscription.check_and_update_status()
        
        if subscription.status != 'active':
            return Response({
                'user_id': str(target_user.id),
                'user_name': target_user.full_name,
                'has_subscription': False,
                'can_serve': False,
                'message': 'Subscription has expired. User must renew to continue receiving meals.'
            })
        
        return Response({
            'user_id': str(target_user.id),
            'user_name': target_user.full_name,
            'has_subscription': True,
            'can_serve': True,
            'days_left': subscription.days_left,
            'remaining_meals': subscription.remaining_meals,
            'end_date': subscription.end_date,
            'plan_name': subscription.plan.name,
            'dietary_plan': {
                'name': subscription.dietary_plan.name,
                'type': subscription.dietary_plan.dietary_type,
                'foods_to_avoid': subscription.dietary_plan.foods_to_avoid,
            } if subscription.dietary_plan else None,
            'message': f'{subscription.days_left} days left in subscription'
        })
