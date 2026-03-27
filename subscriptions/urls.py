"""
URL patterns for subscriptions app.
"""
from django.urls import path
from .views import (
    MySubscriptionView, CreateSubscriptionView,
    SubscriptionHistoryView, CancelSubscriptionView,
    SubscriptionStatusView, DietaryPlanListView, DietaryPlanDetailView,
    AdminSubscriptionListView
)

urlpatterns = [
    path('', CreateSubscriptionView.as_view(), name='subscription-create'),
    path('me/', MySubscriptionView.as_view(), name='my-subscription'),
    path('status/', SubscriptionStatusView.as_view(), name='my-subscription-status'),
    path('status/<uuid:user_id>/', SubscriptionStatusView.as_view(), name='user-subscription-status'),
    path('history/', SubscriptionHistoryView.as_view(), name='subscription-history'),
    path('<uuid:pk>/', CancelSubscriptionView.as_view(), name='subscription-cancel'),
    
    # Dietary plans (public)
    path('dietary-plans/', DietaryPlanListView.as_view(), name='dietary-plan-list'),
    path('dietary-plans/<uuid:pk>/', DietaryPlanDetailView.as_view(), name='dietary-plan-detail'),
    
    # Admin
    path('admin/list/', AdminSubscriptionListView.as_view(), name='admin-subscription-list'),
]
