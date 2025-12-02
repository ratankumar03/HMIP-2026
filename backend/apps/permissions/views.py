from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging

from .models import LocationPermission, PermissionAlert, SafeZone
from .serializers import (
    LocationPermissionRequestSerializer,
    LocationPermissionResponseSerializer,
    LocationPermissionSerializer,
    PermissionAlertSerializer,
    SafeZoneSerializer,
    PermissionStatsSerializer
)
from .tasks import send_permission_request_notification

User = get_user_model()
logger = logging.getLogger(__name__)


class RequestLocationPermissionView(APIView):
    """Request location tracking permission from another user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = LocationPermissionRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            target_phone = serializer.validated_data['target_phone']
            
            try:
                target_user = User.objects.get(phone=target_phone)
                
                if target_user == request.user:
                    return Response({
                        'success': False,
                        'message': 'You cannot track yourself'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check for existing active permission
                existing = LocationPermission.objects.filter(
                    requester=request.user,
                    target=target_user,
                    status__in=['pending', 'approved']
                ).first()
                
                if existing:
                    return Response({
                        'success': False,
                        'message': 'You already have an active request or permission with this user'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create permission request
                duration_hours = serializer.validated_data.get('duration_hours', 24)
                permission = LocationPermission.objects.create(
                    requester=request.user,
                    target=target_user,
                    purpose=serializer.validated_data.get('purpose', ''),
                    expires_at=timezone.now() + timedelta(hours=duration_hours),
                    update_interval=serializer.validated_data.get('update_interval', 30),
                    allow_ai_prediction=serializer.validated_data.get('allow_ai_prediction', True),
                    allow_heatmap=serializer.validated_data.get('allow_heatmap', True),
                    send_alerts=serializer.validated_data.get('send_alerts', True),
                    request_ip=request.META.get('REMOTE_ADDR')
                )
                
                # Send notification to target user
                send_permission_request_notification.delay(permission.id)
                
                return Response({
                    'success': True,
                    'message': 'Permission request sent successfully',
                    'permission': LocationPermissionSerializer(permission).data
                }, status=status.HTTP_201_CREATED)
                
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RespondToPermissionView(APIView):
    """Approve or deny location permission request"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = LocationPermissionResponseSerializer(data=request.data)
        
        if serializer.is_valid():
            permission_id = serializer.validated_data['permission_id']
            approved = serializer.validated_data['approved']
            
            try:
                permission = LocationPermission.objects.get(
                    id=permission_id,
                    target=request.user,
                    status='pending'
                )
                
                if approved:
                    permission.approve()
                    message = 'Permission approved successfully'
                else:
                    permission.deny()
                    message = 'Permission denied'
                
                permission.response_ip = request.META.get('REMOTE_ADDR')
                permission.save()
                
                return Response({
                    'success': True,
                    'message': message,
                    'permission': LocationPermissionSerializer(permission).data
                }, status=status.HTTP_200_OK)
                
            except LocationPermission.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Permission request not found or already responded'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MyPermissionsView(generics.ListAPIView):
    """List all permissions where user is requester"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationPermissionSerializer
    
    def get_queryset(self):
        return LocationPermission.objects.filter(
            requester=self.request.user
        ).order_by('-requested_at')


class PendingPermissionsView(generics.ListAPIView):
    """List all pending permission requests where user is target"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationPermissionSerializer
    
    def get_queryset(self):
        return LocationPermission.objects.filter(
            target=self.request.user,
            status='pending'
        ).order_by('-requested_at')


class ActivePermissionsView(generics.ListAPIView):
    """List all active permissions where user is either requester or target"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationPermissionSerializer
    
    def get_queryset(self):
        return LocationPermission.objects.filter(
            Q(requester=self.request.user) | Q(target=self.request.user),
            status='approved',
            is_active=True
        ).order_by('-requested_at')


class RevokePermissionView(APIView):
    """Revoke an active permission"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, permission_id):
        try:
            permission = LocationPermission.objects.get(
                id=permission_id,
                status='approved',
                is_active=True
            )
            
            # Check if user is requester or target
            if permission.requester != request.user and permission.target != request.user:
                return Response({
                    'success': False,
                    'message': 'You do not have permission to revoke this'
                }, status=status.HTTP_403_FORBIDDEN)
            
            permission.revoke()
            
            return Response({
                'success': True,
                'message': 'Permission revoked successfully'
            }, status=status.HTTP_200_OK)
            
        except LocationPermission.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Permission not found or already inactive'
            }, status=status.HTTP_404_NOT_FOUND)


class PermissionAlertsView(generics.ListAPIView):
    """List all alerts for user's permissions"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PermissionAlertSerializer
    
    def get_queryset(self):
        return PermissionAlert.objects.filter(
            permission__requester=self.request.user
        ).order_by('-created_at')


class SafeZonesView(generics.ListCreateAPIView):
    """List and create safe zones"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SafeZoneSerializer
    
    def get_queryset(self):
        return SafeZone.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PermissionStatsView(APIView):
    """Get permission statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        stats = {
            'total_permissions': LocationPermission.objects.filter(
                Q(requester=user) | Q(target=user)
            ).count(),
            'active_permissions': LocationPermission.objects.filter(
                Q(requester=user) | Q(target=user),
                status='approved',
                is_active=True
            ).count(),
            'pending_requests': LocationPermission.objects.filter(
                target=user,
                status='pending'
            ).count(),
            'total_alerts': PermissionAlert.objects.filter(
                permission__requester=user
            ).count(),
            'unread_alerts': PermissionAlert.objects.filter(
                permission__requester=user,
                is_read=False
            ).count()
        }
        
        serializer = PermissionStatsSerializer(stats)
        return Response({
            'success': True,
            'stats': serializer.data
        })