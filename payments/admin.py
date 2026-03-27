"""
Admin configuration for payments.
"""
from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'user', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_reference', 'external_reference', 'user__full_name', 'user__cps_number']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'subscription']
    readonly_fields = ['payment_reference', 'created_at', 'completed_at']
