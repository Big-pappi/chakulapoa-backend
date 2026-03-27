"""
Admin configuration for users.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['cps_number', 'full_name', 'phone_number', 'role', 'restaurant', 'region', 'is_active']
    list_filter = ['role', 'is_active', 'region']
    search_fields = ['cps_number', 'full_name', 'phone_number', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('cps_number', 'full_name', 'email', 'registration_number')}),
        ('Organization', {'fields': ('restaurant', 'region', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('QR Code', {'fields': ('qr_code_data',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password1', 'password2', 'role', 'restaurant', 'region'),
        }),
    )
