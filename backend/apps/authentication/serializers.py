# 📝 Authentication Serializers
# File Location: backend/apps/authentication/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, OTP, UserSession
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('phone', 'email', 'full_name', 'password', 'password_confirm', 'date_of_birth')
    
    def validate_phone(self, value):
        """Validate phone number format"""
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', value)
        
        if len(phone) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("This phone number is already registered")
        
        return phone
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user account"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            phone=validated_data['phone'],
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    phone = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if phone and password:
            # Clean phone number
            phone = re.sub(r'\D', '', phone)
            
            user = authenticate(phone=phone, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid phone number or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include phone and password")


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request"""
    
    phone = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(
        choices=['verification', 'login', 'permission', 'reset_password'],
        required=True
    )
    
    def validate_phone(self, value):
        """Validate and clean phone number"""
        phone = re.sub(r'\D', '', value)
        if len(phone) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return phone


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    
    phone = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    purpose = serializers.ChoiceField(
        choices=['verification', 'login', 'permission', 'reset_password'],
        required=True
    )
    
    def validate_phone(self, value):
        """Validate and clean phone number"""
        phone = re.sub(r'\D', '', value)
        if len(phone) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return phone
    
    def validate_otp_code(self, value):
        """Validate OTP code format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    class Meta:
        model = User
        fields = (
            'id', 'phone', 'email', 'full_name', 'role', 'is_verified',
            'date_joined', 'last_login', 'profile_picture', 'bio',
            'date_of_birth', 'allow_location_tracking', 'share_location_by_default'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'role')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = (
            'email', 'full_name', 'profile_picture', 'bio',
            'date_of_birth', 'allow_location_tracking', 'share_location_by_default'
        )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions"""
    
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = UserSession
        fields = (
            'id', 'user_phone', 'ip_address', 'user_agent',
            'device_info', 'is_active', 'created_at',
            'last_activity', 'expires_at'
        )
        read_only_fields = fields


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    
    refresh = serializers.CharField(required=True)


class DeviceRegistrationSerializer(serializers.Serializer):
    """Serializer for device registration (FCM token)"""
    
    device_id = serializers.CharField(required=True)
    fcm_token = serializers.CharField(required=True)
    device_info = serializers.JSONField(required=False)