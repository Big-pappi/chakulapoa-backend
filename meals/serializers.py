"""
Serializers for Meal models.
"""
from rest_framework import serializers
from .models import Meal, MealOrder


class MealSerializer(serializers.ModelSerializer):
    """Meal serializer."""
    is_available = serializers.BooleanField(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    # Legacy field for backwards compatibility
    university_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Meal
        fields = [
            'id', 'restaurant', 'restaurant_name', 'university_name', 'name', 'meal_type',
            'description', 'available_date', 'max_servings', 'current_orders',
            'image_url', 'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'current_orders', 'created_at']


class MealOrderSerializer(serializers.ModelSerializer):
    """Meal order serializer."""
    meal = MealSerializer(read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_cps = serializers.CharField(source='user.cps_number', read_only=True)
    served_by_name = serializers.CharField(source='served_by.full_name', read_only=True)
    
    class Meta:
        model = MealOrder
        fields = [
            'id', 'user', 'user_name', 'user_cps', 'meal', 'subscription',
            'order_date', 'status', 'served_at', 'served_by', 'served_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'subscription', 'served_at', 'served_by', 'created_at']


class SelectMealSerializer(serializers.Serializer):
    """Serializer for selecting a meal."""
    meal_id = serializers.UUIDField()
    
    def validate_meal_id(self, value):
        from django.utils import timezone
        try:
            meal = Meal.objects.get(id=value)
            if meal.available_date < timezone.now().date():
                raise serializers.ValidationError("This meal is no longer available.")
            if not meal.is_available:
                raise serializers.ValidationError("This meal has reached maximum orders.")
        except Meal.DoesNotExist:
            raise serializers.ValidationError("Meal not found.")
        return value
    
    def create(self, validated_data):
        from django.utils import timezone
        from subscriptions.models import Subscription
        
        user = self.context['request'].user
        meal = Meal.objects.get(id=validated_data['meal_id'])
        
        # Check if user has active subscription
        subscription = Subscription.objects.filter(
            user=user,
            status='active',
            remaining_meals__gt=0
        ).first()
        
        if not subscription:
            raise serializers.ValidationError("You don't have an active subscription with remaining meals.")
        
        # Check if user already ordered this meal
        if MealOrder.objects.filter(user=user, meal=meal).exists():
            raise serializers.ValidationError("You have already ordered this meal.")
        
        # Create order
        order = MealOrder.objects.create(
            user=user,
            meal=meal,
            subscription=subscription,
            order_date=meal.available_date,
            status='confirmed'
        )
        
        # Update meal order count
        meal.current_orders += 1
        meal.save()
        
        # Deduct from subscription
        subscription.deduct_meal()
        
        return order


class VerifyUserSerializer(serializers.Serializer):
    """Serializer for staff verification of user."""
    cps_number = serializers.CharField(required=False, allow_blank=True)
    qr_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if not data.get('cps_number') and not data.get('qr_code'):
            raise serializers.ValidationError("Please provide CPS number or QR code.")
        return data


# Legacy alias for backwards compatibility
VerifyStudentSerializer = VerifyUserSerializer


class ServeMealSerializer(serializers.Serializer):
    """Serializer for serving a meal."""
    order_id = serializers.UUIDField()
    
    def validate_order_id(self, value):
        try:
            order = MealOrder.objects.get(id=value)
            if order.status == 'served':
                raise serializers.ValidationError("This meal has already been served.")
            if order.status == 'cancelled':
                raise serializers.ValidationError("This order has been cancelled.")
        except MealOrder.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        return value
