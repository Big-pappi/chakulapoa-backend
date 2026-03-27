"""
User models for Chakula Poa.
"""
import uuid
import qrcode
import io
import base64
import random
import string
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager."""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a regular User."""
        if not phone_number:
            raise ValueError('Users must have a phone number')
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.generate_cps_number()
        user.generate_daily_code()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and save a SuperUser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for Chakula Poa."""
    
    ROLE_CHOICES = [
        ('user', 'User'),  # Changed from 'student' to 'user'
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
        ('developer', 'Developer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cps_number = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Changed from university to restaurant
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    
    # Region field for users not tied to a specific restaurant
    region = models.CharField(max_length=50, blank=True, null=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Daily rotating QR code and CPS code (format: CPS#XXXX)
    daily_code = models.CharField(max_length=10, blank=True, null=True)
    daily_code_date = models.DateField(blank=True, null=True)
    qr_code_data = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.cps_number})"
    
    def generate_cps_number(self):
        """Generate a unique permanent CPS number (CPS#XXXX format)."""
        if not self.cps_number:
            prefix = 'CPS#'
            while True:
                # Generate random 4-character alphanumeric code
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                cps = f"{prefix}{code}"
                if not User.objects.filter(cps_number=cps).exists():
                    self.cps_number = cps
                    break
    
    def generate_daily_code(self):
        """Generate daily rotating code (changes at midnight)."""
        today = timezone.now().date()
        
        # Only regenerate if code is missing or from a different day
        if not self.daily_code or self.daily_code_date != today:
            # Generate new daily code in format: CPS#XXXX
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            self.daily_code = f"CPS#{code}"
            self.daily_code_date = today
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate QR code data for the daily code."""
        if self.daily_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # QR code contains the daily code
            qr.add_data(self.daily_code)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            self.qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    def get_current_code(self):
        """Get the current valid daily code, regenerating if needed."""
        today = timezone.now().date()
        if not self.daily_code or self.daily_code_date != today:
            self.generate_daily_code()
            self.save(update_fields=['daily_code', 'daily_code_date', 'qr_code_data'])
        return self.daily_code
    
    @property
    def restaurant_name(self):
        return self.restaurant.name if self.restaurant else None
    
    @property
    def location_type(self):
        return self.restaurant.location_type if self.restaurant else None
    
    # Legacy property for backwards compatibility
    @property
    def university_name(self):
        return self.restaurant_name
