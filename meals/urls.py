"""
URL patterns for meals app.
"""
from django.urls import path
from .views import (
    MealListView, MealDetailView, SelectMealView,
    MyOrdersView, OrderListView, CancelOrderView
)

urlpatterns = [
    path('', MealListView.as_view(), name='meal-list'),
    path('<uuid:pk>/', MealDetailView.as_view(), name='meal-detail'),
    path('select/', SelectMealView.as_view(), name='meal-select'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/me/', MyOrdersView.as_view(), name='my-orders'),
    path('orders/<uuid:pk>/', CancelOrderView.as_view(), name='cancel-order'),
]
