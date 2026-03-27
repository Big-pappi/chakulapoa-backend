"""
Serializers for User model.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    restaurant_name = serializers.CharField(read_only=True)
    location_type = serializers.CharField(read_only=True)
    current_code = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'cps_number', 'full_name', 'email', 'phone_number',
            'registration_number', 'restaurant', 'restaurant_name', 'location_type',
            'region', 'role', 'is_active', 'daily_code', 'qr_code_data', 
            'current_code', 'created_at'
        ]
        read_only_fields = ['id', 'cps_number', 'daily_code', 'qr_code_data', 'created_at']
    
    def get_current_code(self, obj):
        """Get the current valid daily code."""
        return obj.get_current_code()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Accept restaurant_id from frontend (maps to restaurant field)
    restaurant_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'email',
            'registration_number', 'restaurant', 'restaurant_id', 'region', 'password'
        ]
        extra_kwargs = {
            'restaurant': {'required': False, 'allow_null': True},
        }
    
    def validate_phone_number(self, value):
        """Validate phone number is unique."""
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate_restaurant_id(self, value):
        """Validate restaurant_id exists."""
        if value:
            from restaurants.models import Restaurant
            if not Restaurant.objects.filter(id=value).exists():
                raise serializers.ValidationError("Invalid restaurant ID.")
        return value
    
    def create(self, validated_data):
        """Create a new user."""
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        
        # Handle restaurant_id -> restaurant mapping
        restaurant_id = validated_data.pop('restaurant_id', None)
        if restaurant_id and not validated_data.get('restaurant'):
            from restaurants.models import Restaurant
            validated_data['restaurant'] = Restaurant.objects.get(id=restaurant_id)
        
        password = validated_data.pop('password')
        user = User.objects.create_user(
            full_name=full_name,
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login - accepts email or phone."""
    identifier = serializers.CharField(help_text="Email or phone number")
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate login credentials."""
        identifier = data.get('identifier')
        password = data.get('password')
        
        if not identifier or not password:
            raise serializers.ValidationError("Must include email/phone and password.")
        
        # Try to find user by email or phone
        user = None
        
        # Check if identifier looks like an email
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(username=user_obj.phone_number, password=password)
            except User.DoesNotExist:
                pass
        else:
            # Assume it's a phone number
            user = authenticate(username=identifier, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid email/phone or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'registration_number', 'region']


class StaffCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating staff users."""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'restaurant', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'staff'
        user = User.objects.create_user(password=password, **validated_data)
        return user


class AdminCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating admin users."""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'restaurant', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'admin'
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (admin view)."""
    restaurant_name = serializers.CharField(read_only=True)
    location_type = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'cps_number', 'full_name', 'phone_number', 'email',
            'restaurant', 'restaurant_name', 'location_type', 'region',
            'role', 'is_active', 'created_at'
        ]
