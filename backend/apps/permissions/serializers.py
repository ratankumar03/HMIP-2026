# 📝 Permission Serializers
# File Location: backend/apps/permissions/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LocationPermission, PermissionAlert, SafeZone

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for permissions"""
    
    class Meta:
        model = User
        fields = ('id', 'phone', 'full_name', 'profile_picture')
        read_only_fields = fields


class LocationPermissionRequestSerializer(serializers.Serializer):
    """Serializer for requesting location tracking permission"""
    
    target_phone = serializers.CharField(required=True)
    purpose = serializers.CharField(required=False, allow_blank=True)
    duration_hours = serializers.IntegerField(default=24, min_value=1, max_value=168)  # Max 1 week
    update_interval = serializers.IntegerField(default=30, min_value=10, max_value=300)
    allow_ai_prediction = serializers.BooleanField(default=True)
    allow_heatmap = serializers.BooleanField(default=True)
    send_alerts = serializers.BooleanField(default=True)
    
    def validate_target_phone(self, value):
        """Validate target phone exists"""
        import re
        phone = re.sub(r'\D', '', value)
        
        try:
            user = User.objects.get(phone=phone)
            return user.phone
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number not found")


class LocationPermissionResponseSerializer(serializers.Serializer):
    """Serializer for responding to permission request"""
    
    permission_id = serializers.UUIDField(required=True)
    approved = serializers.BooleanField(required=True)


class LocationPermissionSerializer(serializers.ModelSerializer):
    """Complete location permission serializer"""
    
    requester = UserBasicSerializer(read_only=True)
    target = UserBasicSerializer(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = LocationPermission
        fields = (
            'id', 'requester', 'target', 'status', 'purpose',
            'requested_at', 'responded_at', 'expires_at',
            'update_interval', 'allow_ai_prediction', 'allow_heatmap',
            'send_alerts', 'safe_zones', 'is_active',
            'time_remaining', 'is_valid'
        )
        read_only_fields = (
            'id', 'requester', 'target', 'status',
            'requested_at', 'responded_at'
        )
    
    def get_time_remaining(self, obj):
        """Calculate time remaining until expiry"""
        from django.utils import timezone
        
        if obj.expires_at > timezone.now():
            delta = obj.expires_at - timezone.now()
            return {
                'days': delta.days,
                'hours': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60,
                'total_seconds': int(delta.total_seconds())
            }
        return None
    
    def get_is_valid(self, obj):
        """Check if permission is currently valid"""
        return obj.is_valid()


class PermissionAlertSerializer(serializers.ModelSerializer):
    """Serializer for permission alerts"""
    
    permission_id = serializers.UUIDField(source='permission.id', read_only=True)
    requester = UserBasicSerializer(source='permission.requester', read_only=True)
    target = UserBasicSerializer(source='permission.target', read_only=True)
    
    class Meta:
        model = PermissionAlert
        fields = (
            'id', 'permission_id', 'requester', 'target',
            'alert_type', 'severity', 'title', 'message',
            'location', 'metadata', 'is_read', 'is_acknowledged',
            'created_at', 'read_at', 'acknowledged_at'
        )
        read_only_fields = fields


class SafeZoneSerializer(serializers.ModelSerializer):
    """Serializer for safe zones"""
    
    class Meta:
        model = SafeZone
        fields = (
            'id', 'name', 'description', 'latitude', 'longitude',
            'radius', 'is_active', 'send_entry_alert', 'send_exit_alert',
            'active_days', 'active_start_time', 'active_end_time',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_radius(self, value):
        """Validate safe zone radius"""
        if value < 50:
            raise serializers.ValidationError("Radius must be at least 50 meters")
        if value > 5000:
            raise serializers.ValidationError("Radius cannot exceed 5000 meters")
        return value
    
    def validate_latitude(self, value):
        """Validate latitude"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value


class PermissionStatsSerializer(serializers.Serializer):
    """Serializer for permission statistics"""
    
    total_permissions = serializers.IntegerField()
    active_permissions = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    unread_alerts = serializers.IntegerField()