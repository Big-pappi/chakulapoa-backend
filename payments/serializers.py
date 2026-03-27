"""
Serializers for Payment models.
"""
from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer."""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    subscription_name = serializers.CharField(source='subscription.plan.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_name', 'subscription', 'subscription_name',
            'amount', 'currency', 'payment_method', 'payment_reference',
            'external_reference', 'status', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'payment_reference', 'created_at', 'completed_at']


class InitiatePaymentSerializer(serializers.Serializer):
    """Serializer for initiating payment."""
    subscription_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=[
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
    ])
    phone_number = serializers.CharField(max_length=20)
    
    def validate_subscription_id(self, value):
        from subscriptions.models import Subscription
        try:
            subscription = Subscription.objects.get(id=value)
            if subscription.status != 'pending':
                raise serializers.ValidationError("This subscription is not pending payment.")
        except Subscription.DoesNotExist:
            raise serializers.ValidationError("Subscription not found.")
        return value
    
    def create(self, validated_data):
        from subscriptions.models import Subscription
        
        user = self.context['request'].user
        subscription = Subscription.objects.get(id=validated_data['subscription_id'])
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=user,
            subscription=subscription,
            amount=subscription.plan.price,
            payment_method=validated_data['payment_method'],
            payment_reference=Transaction.generate_reference(),
            metadata={
                'phone_number': validated_data['phone_number'],
                'plan_name': subscription.plan.name
            }
        )
        
        # In production, integrate with M-Pesa/Airtel Money API here
        # For now, we simulate successful payment
        # transaction.mark_completed()
        
        return transaction
