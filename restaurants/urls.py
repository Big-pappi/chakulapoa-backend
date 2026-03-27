"""
URL patterns for restaurants app.
"""
from django.urls import path
from .views import (
    RestaurantListView, 
    RestaurantDetailView,
    RestaurantsByRegionView,
    RestaurantAdminListView,
    RestaurantAdminDetailView,
    LocationTypeListView,
    RegionListView
)

urlpatterns = [
    # Public endpoints
    path('', RestaurantListView.as_view(), name='restaurant-list'),
    path('types/', LocationTypeListView.as_view(), name='location-types'),
    path('regions/', RegionListView.as_view(), name='regions'),
    path('by-region/<str:region>/', RestaurantsByRegionView.as_view(), name='restaurants-by-region'),
    path('<uuid:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    
    # Admin endpoints
    path('admin/', RestaurantAdminListView.as_view(), name='restaurant-admin-list'),
    path('admin/<uuid:pk>/', RestaurantAdminDetailView.as_view(), name='restaurant-admin-detail'),
]
