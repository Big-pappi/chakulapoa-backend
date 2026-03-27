"""
Admin configuration for restaurants.
"""
from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location_type', 'region', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'location_type', 'region', 'city']
    search_fields = ['name', 'code', 'city', 'area']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'location_type', 'is_active')
        }),
        ('Location', {
            'fields': ('region', 'city', 'area', 'address')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
