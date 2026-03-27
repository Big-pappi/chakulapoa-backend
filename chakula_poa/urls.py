"""
URL configuration for Chakula Poa project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for Render deployment."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'chakula-poa-api',
        'version': '1.0.0'
    })


urlpatterns = [
    # Health check for Render
    path('api/health/', health_check, name='health-check'),
    
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    
    # Restaurants (locations) - new primary endpoint
    path('api/restaurants/', include('restaurants.urls')),
    # Legacy universities endpoint for backwards compatibility
    path('api/universities/', include('restaurants.urls')),
    
    path('api/plans/', include('subscriptions.urls_plans')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/meals/', include('meals.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/staff/', include('meals.urls_staff')),
    path('api/admin/', include('users.urls_admin')),
    
    # User dashboard - new primary endpoint
    path('api/user/', include('users.urls_users')),
    # Legacy students endpoint for backwards compatibility
    path('api/students/', include('users.urls_users')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
