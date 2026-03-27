"""
URL patterns for admin endpoints.
"""
from django.urls import path
from .views import (
    AdminDashboardView, AdminUserListView,
    AdminStaffListView, AdminStaffDetailView,
    DemandReportView, RevenueReportView,
    SuperAdminUserListView, SuperAdminCreateAdminView,
    SuperAdminSystemStatsView, VerifyUserCodeView,
    SuperAdminResetPasswordView, SuperAdminUpdateUserView
)
from meals.views import AdminMealListView, AdminMealDetailView
from restaurants.views import RestaurantAdminListView, RestaurantAdminDetailView

urlpatterns = [
    # Admin Dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Users (previously students)
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    # Legacy alias for backwards compatibility
    path('students/', AdminUserListView.as_view(), name='admin-students'),
    
    # Verify user code
    path('verify-code/', VerifyUserCodeView.as_view(), name='verify-code'),
    
    # Staff
    path('staff/', AdminStaffListView.as_view(), name='admin-staff-list'),
    path('staff/<uuid:pk>/', AdminStaffDetailView.as_view(), name='admin-staff-detail'),
    
    # Meals
    path('meals/', AdminMealListView.as_view(), name='admin-meals-list'),
    path('meals/<uuid:pk>/', AdminMealDetailView.as_view(), name='admin-meals-detail'),
    
    # Reports
    path('reports/demand/', DemandReportView.as_view(), name='demand-report'),
    path('reports/revenue/', RevenueReportView.as_view(), name='revenue-report'),
    
    # Super Admin - Restaurants (previously universities)
    path('restaurants/', RestaurantAdminListView.as_view(), name='admin-restaurants-list'),
    path('restaurants/<uuid:pk>/', RestaurantAdminDetailView.as_view(), name='admin-restaurants-detail'),
    # Legacy alias for backwards compatibility
    path('universities/', RestaurantAdminListView.as_view(), name='admin-universities-list'),
    path('universities/<uuid:pk>/', RestaurantAdminDetailView.as_view(), name='admin-universities-detail'),
    
    # Super Admin - System
    path('system/stats/', SuperAdminSystemStatsView.as_view(), name='super-admin-stats'),
    path('all-users/', SuperAdminUserListView.as_view(), name='super-admin-users'),
    path('admins/', SuperAdminCreateAdminView.as_view(), name='super-admin-create-admin'),
    
    # Super Admin - User Management
    path('users/<uuid:pk>/', SuperAdminUpdateUserView.as_view(), name='super-admin-user-detail'),
    path('users/<uuid:pk>/reset-password/', SuperAdminResetPasswordView.as_view(), name='super-admin-reset-password'),
]
