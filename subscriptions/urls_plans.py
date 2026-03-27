"""
URL patterns for subscription plans.
"""
from django.urls import path
from .views import SubscriptionPlanListView, SubscriptionPlanDetailView

urlpatterns = [
    path('', SubscriptionPlanListView.as_view(), name='plan-list'),
    path('<uuid:pk>/', SubscriptionPlanDetailView.as_view(), name='plan-detail'),
]
