"""
Serializers for Subscription models.
"""
from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, DietaryPlan


class DietaryPlanSerializer(serializers.ModelSerializer):
    """Dietary plan serializer."""
    dietary_type_display = serializers.CharField(source='get_dietary_type_display', read_only=True)
    
    class Meta:
        model = DietaryPlan
        fields = [
            'id', 'name', 'dietary_type', 'dietary_type_display', 'description',
            'foods_to_avoid', 'recommended_foods', 'additional_price', 'is_active'
        ]
        read_only_fields = ['id']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Subscription plan serializer."""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'restaurant', 'restaurant_name', 'name', 'duration_type',
            'duration_days', 'price', 'meals_per_day', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer."""
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True, source='plan.id')
    dietary_plan = DietaryPlanSerializer(read_only=True)
    dietary_plan_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    days_left = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_name', 'plan', 'plan_id', 'dietary_plan', 'dietary_plan_id',
            'start_date', 'end_date', 'status', 'remaining_meals', 'days_left',
            'total_price', 'is_expired', 'payment_reference', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'start_date', 'end_date', 'remaining_meals', 'created_at']


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating a subscription."""
    plan_id = serializers.UUIDField()
    dietary_plan_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_plan_id(self, value):
        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive plan.")
        return value
    
    def validate_dietary_plan_id(self, value):
        if value:
            try:
                DietaryPlan.objects.get(id=value, is_active=True)
            except DietaryPlan.DoesNotExist:
                raise serializers.ValidationError("Invalid or inactive dietary plan.")
        return value
    
    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        
        user = self.context['request'].user
        plan = SubscriptionPlan.objects.get(id=validated_data['plan_id'])
        
        # Get dietary plan if specified
        dietary_plan = None
        dietary_plan_id = validated_data.get('dietary_plan_id')
        if dietary_plan_id:
            dietary_plan = DietaryPlan.objects.get(id=dietary_plan_id)
        
        # Create pending subscription
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            dietary_plan=dietary_plan,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=plan.duration_days),
            status='pending',
            remaining_meals=plan.meals_per_day * plan.duration_days
        )
        return subscription


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing subscriptions (admin view)."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    dietary_plan_name = serializers.CharField(source='dietary_plan.name', read_only=True)
    days_left = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'plan_name', 'dietary_plan_name',
            'start_date', 'end_date', 'status', 'remaining_meals', 'days_left', 'created_at'
        ]
