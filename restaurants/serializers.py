"""
Serializers for Restaurant model.
"""
from rest_framework import serializers
from .models import Restaurant, LocationType, TANZANIA_REGIONS


class RestaurantSerializer(serializers.ModelSerializer):
    """Restaurant serializer."""
    location_type_display = serializers.CharField(read_only=True)
    region_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'code', 'location_type', 'location_type_display',
            'region', 'region_display', 'area', 'address', 'city',
            'contact_email', 'contact_phone', 'capacity', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RestaurantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating restaurants."""
    
    class Meta:
        model = Restaurant
        fields = [
            'name', 'code', 'location_type', 'region', 'area',
            'address', 'city', 'contact_email', 'contact_phone', 'capacity'
        ]
    
    def validate_code(self, value):
        """Ensure code is unique and uppercase."""
        value = value.upper()
        if Restaurant.objects.filter(code=value).exists():
            raise serializers.ValidationError("A location with this code already exists.")
        return value


class LocationTypeSerializer(serializers.Serializer):
    """Serializer for location types."""
    value = serializers.CharField()
    label = serializers.CharField()


class RegionSerializer(serializers.Serializer):
    """Serializer for Tanzania regions."""
    value = serializers.CharField()
    label = serializers.CharField()
