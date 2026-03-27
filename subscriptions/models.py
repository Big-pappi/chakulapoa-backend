"""
Subscription models for Chakula Poa.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class DietaryPlan(models.Model):
    """
    Dietary plan for users with special food requirements.
    Examples: ulcer diet, diabetic diet, vegetarian, halal, etc.
    """
    
    DIETARY_TYPE_CHOICES = [
        ('ulcer', 'Ulcer Diet'),
        ('diabetic', 'Diabetic Diet'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('halal', 'Halal'),
        ('gluten_free', 'Gluten Free'),
        ('low_sodium', 'Low Sodium'),
        ('renal', 'Renal Diet'),
        ('heart_healthy', 'Heart Healthy'),
        ('pregnancy', 'Pregnancy Diet'),
        ('other', 'Other Special Diet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    dietary_type = models.CharField(max_length=30, choices=DIETARY_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Foods to avoid
    foods_to_avoid = models.TextField(
        blank=True, 
        null=True,
        help_text="List of foods to avoid (comma separated)"
    )
    
    # Recommended foods
    recommended_foods = models.TextField(
        blank=True, 
        null=True,
        help_text="List of recommended foods (comma separated)"
    )
    
    # Additional price per month for special dietary requirements
    additional_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Additional cost per month for this dietary plan"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dietary_plans'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_dietary_type_display()})"


class SubscriptionPlan(models.Model):
    """Subscription plan model."""
    
    DURATION_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('semester', 'Semester'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='plans',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)  # e.g., "1 Month Plan", "Full Semester"
    duration_type = models.CharField(max_length=20, choices=DURATION_CHOICES)
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in TZS
    meals_per_day = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price']
    
    def __str__(self):
        location = self.restaurant.code if self.restaurant else "Global"
        return f"{self.name} - {location} (TZS {self.price})"


class Subscription(models.Model):
    """User subscription model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Dietary plan for special food requirements
    dietary_plan = models.ForeignKey(
        DietaryPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions',
        help_text="Special dietary requirements for this subscription"
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remaining_meals = models.IntegerField()
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.plan.name} ({self.status})"
    
    @property
    def days_left(self):
        """Calculate days left in subscription."""
        if self.status != 'active':
            return 0
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    @property
    def is_expired(self):
        """Check if subscription has expired."""
        return self.days_left <= 0 and self.status == 'active'
    
    @property
    def total_price(self):
        """Calculate total price including dietary plan additional cost."""
        base_price = self.plan.price
        if self.dietary_plan:
            # Calculate months and add dietary plan cost
            months = max(1, self.plan.duration_days // 30)
            return base_price + (self.dietary_plan.additional_price * months)
        return base_price
    
    def check_and_update_status(self):
        """Check and update subscription status if expired."""
        if self.is_expired:
            self.status = 'expired'
            self.save(update_fields=['status'])
            return True
        return False
    
    def activate(self):
        """Activate the subscription."""
        from datetime import timedelta
        
        self.status = 'active'
        self.start_date = timezone.now().date()
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        self.remaining_meals = self.plan.meals_per_day * self.plan.duration_days
        self.save()
    
    def deduct_meal(self):
        """Deduct one meal from remaining meals."""
        if self.remaining_meals > 0:
            self.remaining_meals -= 1
            self.save()
            return True
        return False
