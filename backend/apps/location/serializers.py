# 📝 Location Serializers
# File Location: backend/apps/location/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LocationData, LocationHistory

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for location data"""

    class Meta:
        model = User
        fields = ('id', 'phone', 'full_name', 'profile_picture')
        read_only_fields = fields


class LocationDataSerializer(serializers.ModelSerializer):
    """Serializer for location data"""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = LocationData
        fields = (
            'id', 'user', 'latitude', 'longitude', 'altitude', 'accuracy',
            'speed', 'heading', 'battery_level', 'is_moving', 'activity_type',
            'timestamp', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')


class LocationDataCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating location data"""

    class Meta:
        model = LocationData
        fields = (
            'latitude', 'longitude', 'altitude', 'accuracy',
            'speed', 'heading', 'battery_level', 'is_moving', 'activity_type',
            'timestamp'
        )

    def validate_latitude(self, value):
        """Validate latitude range"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        """Validate longitude range"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

    def validate_accuracy(self, value):
        """Validate accuracy is positive"""
        if value < 0:
            raise serializers.ValidationError("Accuracy must be positive")
        return value

    def validate_battery_level(self, value):
        """Validate battery level range"""
        if value is not None and not 0 <= value <= 100:
            raise serializers.ValidationError("Battery level must be between 0 and 100")
        return value


class LocationHistorySerializer(serializers.ModelSerializer):
    """Serializer for location history"""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = LocationHistory
        fields = (
            'id', 'user', 'date', 'total_distance', 'avg_speed', 'max_speed',
            'time_stationary', 'time_walking', 'time_driving',
            'unique_locations', 'frequent_locations',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class LocationQuerySerializer(serializers.Serializer):
    """Serializer for location query parameters"""

    user_id = serializers.UUIDField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    limit = serializers.IntegerField(default=100, min_value=1, max_value=1000)

    def validate(self, attrs):
        """Validate date range"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "start_date": "Start date must be before end date"
            })

        return attrs


class LocationStatsSerializer(serializers.Serializer):
    """Serializer for location statistics"""

    total_locations = serializers.IntegerField()
    last_location_time = serializers.DateTimeField(allow_null=True)
    total_distance_today = serializers.FloatField()
    avg_speed_today = serializers.FloatField()
    locations_today = serializers.IntegerField()
