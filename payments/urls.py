"""
URL patterns for payments app.
"""
from django.urls import path
from .views import (
    InitiatePaymentView, PaymentStatusView,
    PaymentHistoryView, PaymentCallbackView
)

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('<uuid:payment_id>/status/', PaymentStatusView.as_view(), name='payment-status'),
    path('history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]
