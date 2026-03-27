"""
Views for Restaurant management.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Restaurant, LocationType, TANZANIA_REGIONS
from .serializers import (
    RestaurantSerializer, 
    RestaurantCreateSerializer,
    LocationTypeSerializer,
    RegionSerializer
)
from users.views import IsSuperAdmin, IsAdminOrAbove


class RestaurantFilter(filters.FilterSet):
    """Filter for restaurants."""
    location_type = filters.ChoiceFilter(choices=LocationType.choices)
    region = filters.ChoiceFilter(choices=TANZANIA_REGIONS)
    is_active = filters.BooleanFilter()
    search = filters.CharFilter(method='filter_search')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(code__icontains=value)
    
    class Meta:
        model = Restaurant
        fields = ['location_type', 'region', 'is_active']


class RestaurantListView(generics.ListAPIView):
    """List all active restaurants (public)."""
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = RestaurantFilter


class RestaurantDetailView(generics.RetrieveAPIView):
    """Get restaurant details (public)."""
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]


class RestaurantsByRegionView(generics.ListAPIView):
    """List restaurants by region (public)."""
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        region = self.kwargs.get('region')
        return Restaurant.objects.filter(is_active=True, region=region)


class RestaurantAdminListView(generics.ListCreateAPIView):
    """List and create restaurants (super admin only)."""
    queryset = Restaurant.objects.all()
    permission_classes = [IsSuperAdmin]
    filterset_class = RestaurantFilter
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RestaurantCreateSerializer
        return RestaurantSerializer


class RestaurantAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete restaurant (super admin only)."""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsSuperAdmin]


class LocationTypeListView(APIView):
    """List all location types."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in LocationType.choices
        ]
        return Response(types)


class RegionListView(APIView):
    """List all Tanzania regions."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        regions = [
            {'value': region[0], 'label': region[1]}
            for region in TANZANIA_REGIONS
        ]
        return Response(regions)
