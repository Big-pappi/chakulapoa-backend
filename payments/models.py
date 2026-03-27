"""
Payment/Transaction models for Chakula Poa.
"""
import uuid
from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """Transaction model for payments."""
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('airtel_money', 'Airtel Money'),
        ('selcom', 'Selcom'),
        ('bank', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TZS')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, unique=True)
    external_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - TZS {self.amount} ({self.status})"
    
    def mark_completed(self, external_reference=None):
        """Mark transaction as completed."""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        if external_reference:
            self.external_reference = external_reference
        self.save()
        
        # Activate subscription if pending
        if self.subscription and self.subscription.status == 'pending':
            self.subscription.activate()
    
    @classmethod
    def generate_reference(cls):
        """Generate unique payment reference."""
        import random
        import string
        prefix = 'CPS'
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return f"{prefix}{random_part}"
