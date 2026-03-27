"""
Admin configuration for universities.
"""
from django.contrib import admin
from .models import University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'code', 'city']
    ordering = ['name']
