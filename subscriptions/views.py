"""
Views for Subscription management.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SubscriptionPlan, Subscription, DietaryPlan
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer,
    CreateSubscriptionSerializer, DietaryPlanSerializer,
    SubscriptionListSerializer
)


# Dietary Plan Views
class DietaryPlanListView(generics.ListAPIView):
    """List all active dietary plans."""
    serializer_class = DietaryPlanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return DietaryPlan.objects.filter(is_active=True)


class DietaryPlanDetailView(generics.RetrieveAPIView):
    """Get dietary plan details."""
    queryset = DietaryPlan.objects.filter(is_active=True)
    serializer_class = DietaryPlanSerializer
    permission_classes = [permissions.AllowAny]


# Subscription Plan Views
class SubscriptionPlanListView(generics.ListAPIView):
    """List all active subscription plans."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = SubscriptionPlan.objects.filter(is_active=True)
        # Support both restaurant_id and legacy university_id
        restaurant_id = self.request.query_params.get('restaurant_id') or self.request.query_params.get('university_id')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """Get subscription plan details."""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


# User Subscription Views
class MySubscriptionView(APIView):
    """Get current user's active subscription with days left."""
    
    def get(self, request):
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).select_related('plan', 'dietary_plan').first()
        
        if subscription:
            # Check and update if expired
            subscription.check_and_update_status()
            if subscription.status == 'active':
                return Response(SubscriptionSerializer(subscription).data)
        return Response(None)


class CreateSubscriptionView(generics.CreateAPIView):
    """Create a new subscription."""
    serializer_class = CreateSubscriptionSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )


class SubscriptionHistoryView(generics.ListAPIView):
    """Get user's subscription history."""
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related('plan', 'dietary_plan')


class SubscriptionStatusView(APIView):
    """Get subscription status with days left for users and staff."""
    
    def get(self, request, user_id=None):
        """Get subscription status. If user_id provided (staff), check that user."""
        from users.models import User
        
        if user_id:
            # Staff checking a user's subscription
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            target_user = request.user
        
        subscription = Subscription.objects.filter(
            user=target_user,
            status='active'
        ).select_related('plan', 'dietary_plan').first()
        
        if not subscription:
            return Response({
                'has_subscription': False,
                'message': 'No active subscription',
                'can_be_served': False
            })
        
        # Check if expired
        subscription.check_and_update_status()
        
        return Response({
            'has_subscription': subscription.status == 'active',
            'days_left': subscription.days_left,
            'remaining_meals': subscription.remaining_meals,
            'end_date': subscription.end_date,
            'plan_name': subscription.plan.name,
            'dietary_plan': subscription.dietary_plan.name if subscription.dietary_plan else None,
            'can_be_served': subscription.status == 'active' and subscription.days_left > 0,
            'status': subscription.status
        })


class CancelSubscriptionView(APIView):
    """Cancel a subscription."""
    
    def delete(self, request, pk):
        try:
            subscription = Subscription.objects.get(id=pk, user=request.user)
            if subscription.status == 'pending':
                subscription.status = 'cancelled'
                subscription.save()
                return Response({'message': 'Subscription cancelled'})
            return Response(
                {'detail': 'Cannot cancel an active subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# Admin views
from users.views import IsAdminUser, IsSuperAdmin


class AdminPlanListView(generics.ListCreateAPIView):
    """List and create subscription plans (admin only)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            return SubscriptionPlan.objects.filter(restaurant=user.restaurant)
        return SubscriptionPlan.objects.all()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            serializer.save(restaurant=user.restaurant)
        else:
            serializer.save()


class AdminPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete subscription plan (admin only)."""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' and user.restaurant:
            return SubscriptionPlan.objects.filter(restaurant=user.restaurant)
        return SubscriptionPlan.objects.all()


# Dietary Plan Admin Views
class AdminDietaryPlanListView(generics.ListCreateAPIView):
    """List and create dietary plans (super admin only)."""
    serializer_class = DietaryPlanSerializer
    permission_classes = [IsSuperAdmin]
    queryset = DietaryPlan.objects.all()


class AdminDietaryPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete dietary plan (super admin only)."""
    serializer_class = DietaryPlanSerializer
    permission_classes = [IsSuperAdmin]
    queryset = DietaryPlan.objects.all()


class AdminSubscriptionListView(generics.ListAPIView):
    """List all subscriptions for admin view."""
    serializer_class = SubscriptionListSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Subscription.objects.all().select_related('user', 'plan', 'dietary_plan')
        
        if user.role == 'admin' and user.restaurant:
            queryset = queryset.filter(user__restaurant=user.restaurant)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
