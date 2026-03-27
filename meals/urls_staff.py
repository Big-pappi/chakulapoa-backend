"""
URL patterns for staff endpoints.
"""
from django.urls import path
from .views import (
    StaffVerifyView, StaffServeMealView,
    StaffTodaysOrdersView, StaffStatsView,
    StaffServiceHistoryView, StaffUserSubscriptionCheckView
)

urlpatterns = [
    path('verify/', StaffVerifyView.as_view(), name='staff-verify'),
    path('serve/', StaffServeMealView.as_view(), name='staff-serve'),
    path('orders/today/', StaffTodaysOrdersView.as_view(), name='staff-today-orders'),
    path('stats/', StaffStatsView.as_view(), name='staff-stats'),
    path('history/', StaffServiceHistoryView.as_view(), name='staff-service-history'),
    path('user/<uuid:user_id>/subscription/', StaffUserSubscriptionCheckView.as_view(), name='staff-user-subscription'),
]
