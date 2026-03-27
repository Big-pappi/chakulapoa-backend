"""
Meal models for Chakula Poa.

Meal Time Windows (configurable per restaurant):
- Morning Tea: 6:00 AM - 10:00 AM (1 serving per user)
- Lunch: 11:30 AM - 2:30 PM (1 serving per user)
- Evening: 5:00 PM - 8:00 PM (1 serving per user)
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class MealType(models.TextChoices):
    """Meal type choices matching documentation."""
    TEA = 'tea', 'Morning Tea'
    LUNCH = 'lunch', 'Lunch'
    EVENING = 'evening', 'Evening'


# Default meal windows (in minutes from midnight)
MEAL_WINDOWS = {
    'tea': {'start': 360, 'end': 600},      # 6:00 AM - 10:00 AM
    'lunch': {'start': 690, 'end': 870},    # 11:30 AM - 2:30 PM
    'evening': {'start': 1020, 'end': 1200},  # 5:00 PM - 8:00 PM
}


class Meal(models.Model):
    """Meal model."""
    
    # Legacy choices for backwards compatibility
    MEAL_TYPE_CHOICES = [
        ('tea', 'Morning Tea'),
        ('lunch', 'Lunch'),
        ('evening', 'Evening'),
        # Legacy types
        ('breakfast', 'Breakfast'),
        ('dinner', 'Dinner'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='meals',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=255)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    available_date = models.DateField()
    max_servings = models.IntegerField(default=100)
    current_orders = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meals'
        ordering = ['available_date', 'meal_type']
    
    def __str__(self):
        return f"{self.name} ({self.meal_type}) - {self.available_date}"
    
    @property
    def is_available(self):
        return self.current_orders < self.max_servings
    
    @property
    def is_within_time_window(self):
        """Check if current time is within this meal's service window."""
        if self.meal_type not in MEAL_WINDOWS:
            return True
        
        now = timezone.localtime()
        current_minutes = now.hour * 60 + now.minute
        window = MEAL_WINDOWS[self.meal_type]
        return window['start'] <= current_minutes <= window['end']
    
    @staticmethod
    def get_current_meal_type():
        """Get the current meal type based on time of day."""
        now = timezone.localtime()
        current_minutes = now.hour * 60 + now.minute
        
        for meal_type, window in MEAL_WINDOWS.items():
            if window['start'] <= current_minutes <= window['end']:
                return meal_type
        return None


class MealOrder(models.Model):
    """
    Meal order model.
    
    Constraints:
    - One meal per type per user per day (tea, lunch, evening)
    - Time-locked: only valid during meal window
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('served', 'Served'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_orders'
    )
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True
    )
    # Store meal_type directly for validation (one per type per day)
    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
        default=MealType.LUNCH
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='meal_orders',
        null=True,
        blank=True
    )
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.CASCADE,
        related_name='meal_orders',
        null=True,
        blank=True
    )
    order_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    served_at = models.DateTimeField(blank=True, null=True)
    served_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='served_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meal_orders'
        ordering = ['-created_at']
        # One meal per type per user per day!
        unique_together = ['user', 'meal_type', 'order_date']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.meal_type} ({self.status})"
    
    def mark_served(self, staff_user):
        """Mark the order as served."""
        self.status = 'served'
        self.served_at = timezone.now()
        self.served_by = staff_user
        self.save()
    
    @classmethod
    def has_been_served_today(cls, user, meal_type):
        """Check if user has already been served this meal type today."""
        today = timezone.now().date()
        return cls.objects.filter(
            user=user,
            meal_type=meal_type,
            order_date=today,
            status='served'
        ).exists()
    
    @classmethod
    def can_order(cls, user, meal_type):
        """Check if user can order this meal type today."""
        today = timezone.now().date()
        return not cls.objects.filter(
            user=user,
            meal_type=meal_type,
            order_date=today
        ).exists()
