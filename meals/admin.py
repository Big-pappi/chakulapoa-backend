"""
Admin configuration for meals.
"""
from django.contrib import admin
from .models import Meal, MealOrder


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'meal_type', 'available_date', 'max_servings', 'current_orders']
    list_filter = ['restaurant', 'meal_type', 'available_date']
    search_fields = ['name', 'description']
    ordering = ['-available_date', 'meal_type']


@admin.register(MealOrder)
class MealOrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal', 'meal_type', 'order_date', 'status', 'served_at', 'served_by']
    list_filter = ['status', 'order_date', 'restaurant']
    search_fields = ['user__full_name', 'user__cps_number']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'meal', 'subscription', 'served_by', 'restaurant']
