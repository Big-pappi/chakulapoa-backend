"""
Views for University management.
"""
from rest_framework import generics, permissions
from .models import University
from .serializers import UniversitySerializer
from users.views import IsSuperAdmin


class UniversityListView(generics.ListAPIView):
    """List all active universities (public)."""
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny]


class UniversityDetailView(generics.RetrieveAPIView):
    """Get university details (public)."""
    queryset = University.objects.filter(is_active=True)
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny]


class UniversityAdminListView(generics.ListCreateAPIView):
    """List and create universities (super admin only)."""
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsSuperAdmin]


class UniversityAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete university (super admin only)."""
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsSuperAdmin]
