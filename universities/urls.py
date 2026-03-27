"""
URL patterns for universities app.
"""
from django.urls import path
from .views import UniversityListView, UniversityDetailView

urlpatterns = [
    path('', UniversityListView.as_view(), name='university-list'),
    path('<uuid:pk>/', UniversityDetailView.as_view(), name='university-detail'),
]
