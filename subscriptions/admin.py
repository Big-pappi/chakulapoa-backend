"""
Admin configuration for subscriptions.
"""
from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'duration_type', 'duration_days', 'price', 'meals_per_day', 'is_active']
    list_filter = ['restaurant', 'duration_type', 'is_active']
    search_fields = ['name', 'restaurant__name']
    ordering = ['restaurant', 'price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'remaining_meals']
    list_filter = ['status', 'plan__restaurant']
    search_fields = ['user__full_name', 'user__cps_number', 'payment_reference']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'plan']
