# 📍 Location Views
# File Location: backend/apps/location/views.py

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max, Sum
from datetime import timedelta, date
import logging

from .models import LocationData, LocationHistory
from .serializers import (
    LocationDataSerializer,
    LocationDataCreateSerializer,
    LocationHistorySerializer,
    LocationQuerySerializer,
    LocationStatsSerializer
)
from .mongodb_service import LocationMongoService

User = get_user_model()
logger = logging.getLogger(__name__)


class SubmitLocationView(APIView):
    """
    POST: Submit current location data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LocationDataCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Store in MongoDB for flexible querying
                mongo_service = LocationMongoService()
                location_id = mongo_service.store_location(
                    user_id=str(request.user.id),
                    latitude=serializer.validated_data['latitude'],
                    longitude=serializer.validated_data['longitude'],
                    accuracy=serializer.validated_data.get('accuracy'),
                    metadata={
                        'altitude': serializer.validated_data.get('altitude'),
                        'speed': serializer.validated_data.get('speed'),
                        'heading': serializer.validated_data.get('heading'),
                        'battery_level': serializer.validated_data.get('battery_level'),
                        'is_moving': serializer.validated_data.get('is_moving', True),
                        'activity_type': serializer.validated_data.get('activity_type'),
                    }
                )

                # Also store in SQLite for Django ORM access
                location = serializer.save(user=request.user)

                logger.info(f"Location stored for user {request.user.phone}: {location.latitude}, {location.longitude}")

                return Response({
                    'success': True,
                    'message': 'Location submitted successfully',
                    'location': LocationDataSerializer(location).data
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error storing location: {str(e)}")
                return Response({
                    'success': False,
                    'message': 'Failed to store location'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MyLocationsView(generics.ListAPIView):
    """
    GET: List current user's location history
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationDataSerializer

    def get_queryset(self):
        queryset = LocationData.objects.filter(user=self.request.user)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        # Limit results
        limit = int(self.request.query_params.get('limit', 100))
        return queryset[:limit]


class UserLocationView(APIView):
    """
    GET: Get location data for a specific user (with permission check)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)

            # Check if requester has permission to view this user's location
            from apps.permissions.models import LocationPermission

            has_permission = LocationPermission.objects.filter(
                requester=request.user,
                target=target_user,
                status='approved',
                is_active=True,
                expires_at__gt=timezone.now()
            ).exists()

            if not has_permission and target_user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to view this user\'s location'
                }, status=status.HTTP_403_FORBIDDEN)

            # Get latest location
            latest_location = LocationData.objects.filter(
                user=target_user
            ).order_by('-timestamp').first()

            if not latest_location:
                return Response({
                    'success': True,
                    'message': 'No location data found',
                    'location': None
                }, status=status.HTTP_200_OK)

            return Response({
                'success': True,
                'location': LocationDataSerializer(latest_location).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class UserLocationHistoryView(APIView):
    """
    GET: Get location history for a specific user (with permission check)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)

            # Check if requester has permission to view this user's location
            from apps.permissions.models import LocationPermission

            has_permission = LocationPermission.objects.filter(
                requester=request.user,
                target=target_user,
                status='approved',
                is_active=True,
                expires_at__gt=timezone.now()
            ).exists()

            if not has_permission and target_user != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to view this user\'s location history'
                }, status=status.HTTP_403_FORBIDDEN)

            # Get location history
            queryset = LocationData.objects.filter(user=target_user)

            # Filter by date range
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)

            # Limit results
            limit = int(request.query_params.get('limit', 100))
            locations = queryset[:limit]

            return Response({
                'success': True,
                'count': locations.count(),
                'locations': LocationDataSerializer(locations, many=True).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class LatestLocationView(APIView):
    """
    GET: Get user's latest location
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        latest_location = LocationData.objects.filter(
            user=request.user
        ).order_by('-timestamp').first()

        if not latest_location:
            return Response({
                'success': True,
                'message': 'No location data found',
                'location': None
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True,
            'location': LocationDataSerializer(latest_location).data
        }, status=status.HTTP_200_OK)


class LocationStatsView(APIView):
    """
    GET: Get location statistics for current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Total locations count
        total_locations = LocationData.objects.filter(user=user).count()

        # Last location time
        latest_location = LocationData.objects.filter(user=user).order_by('-timestamp').first()
        last_location_time = latest_location.timestamp if latest_location else None

        # Today's statistics
        today_locations = LocationData.objects.filter(
            user=user,
            timestamp__date=today
        )

        locations_today = today_locations.count()

        # Get today's history if exists
        try:
            today_history = LocationHistory.objects.get(user=user, date=today)
            total_distance_today = today_history.total_distance
            avg_speed_today = today_history.avg_speed
        except LocationHistory.DoesNotExist:
            total_distance_today = 0.0
            avg_speed_today = 0.0

        stats = {
            'total_locations': total_locations,
            'last_location_time': last_location_time,
            'total_distance_today': total_distance_today,
            'avg_speed_today': avg_speed_today,
            'locations_today': locations_today
        }

        serializer = LocationStatsSerializer(stats)

        return Response({
            'success': True,
            'stats': serializer.data
        }, status=status.HTTP_200_OK)


class LocationHistoryListView(generics.ListAPIView):
    """
    GET: List location history aggregates
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationHistorySerializer

    def get_queryset(self):
        queryset = LocationHistory.objects.filter(user=self.request.user)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.order_by('-date')


class DeleteLocationView(APIView):
    """
    DELETE: Delete a specific location entry
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, location_id):
        try:
            location = LocationData.objects.get(
                id=location_id,
                user=request.user
            )
            location.delete()

            return Response({
                'success': True,
                'message': 'Location deleted successfully'
            }, status=status.HTTP_200_OK)

        except LocationData.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Location not found or you do not have permission to delete it'
            }, status=status.HTTP_404_NOT_FOUND)


class DeleteAllLocationsView(APIView):
    """
    DELETE: Delete all location history for current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        count = LocationData.objects.filter(user=request.user).delete()[0]

        return Response({
            'success': True,
            'message': f'Deleted {count} location entries'
        }, status=status.HTTP_200_OK)
