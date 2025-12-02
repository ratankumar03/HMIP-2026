# 🔒 Permission Management Models
# File Location: backend/apps/permissions/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class LocationPermission(models.Model):
    """Model for managing location tracking permissions"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Requester - person who wants to track
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tracking_requests'
    )
    
    # Target - person being tracked
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tracking_permissions'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Permission details
    purpose = models.TextField(blank=True, help_text="Reason for tracking request")
    
    # Time management
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    # Tracking settings
    update_interval = models.IntegerField(
        default=30,
        help_text="Location update interval in seconds"
    )
    
    allow_ai_prediction = models.BooleanField(default=True)
    allow_heatmap = models.BooleanField(default=True)
    send_alerts = models.BooleanField(default=True)
    
    # Safe zones
    safe_zones = models.JSONField(default=list, blank=True)
    
    # Metadata
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    response_ip = models.GenericIPAddressField(null=True, blank=True)
    
    is_active = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'location_permissions'
        verbose_name = 'Location Permission'
        verbose_name_plural = 'Location Permissions'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['target', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['requester', 'target']
    
    def __str__(self):
        return f"{self.requester.phone} tracking {self.target.phone} - {self.status}"
    
    def is_valid(self):
        """Check if permission is still valid"""
        return (
            self.status == 'approved' and
            self.is_active and
            self.expires_at > timezone.now()
        )
    
    def approve(self):
        """Approve the permission request"""
        self.status = 'approved'
        self.is_active = True
        self.responded_at = timezone.now()
        self.save()
    
    def deny(self):
        """Deny the permission request"""
        self.status = 'denied'
        self.is_active = False
        self.responded_at = timezone.now()
        self.save()
    
    def revoke(self):
        """Revoke an active permission"""
        self.status = 'revoked'
        self.is_active = False
        self.save()
    
    def extend_expiry(self, hours=24):
        """Extend permission expiry time"""
        self.expires_at = timezone.now() + timedelta(hours=hours)
        self.save()
    
    def check_expiry(self):
        """Check and update if permission has expired"""
        if self.expires_at < timezone.now() and self.is_active:
            self.status = 'expired'
            self.is_active = False
            self.save()
            return True
        return False


class PermissionAlert(models.Model):
    """Alerts generated from permission tracking"""
    
    ALERT_TYPES = (
        ('entry', 'Entered Safe Zone'),
        ('exit', 'Exited Safe Zone'),
        ('stop', 'Stopped Moving'),
        ('speed', 'Speeding Detected'),
        ('anomaly', 'Anomalous Behavior'),
        ('battery', 'Low Battery'),
        ('offline', 'Device Offline'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permission = models.ForeignKey(
        LocationPermission,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    location = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_acknowledged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'permission_alerts'
        verbose_name = 'Permission Alert'
        verbose_name_plural = 'Permission Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['permission', 'is_read']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.title}"
    
    def mark_as_read(self):
        """Mark alert as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def acknowledge(self):
        """Acknowledge the alert"""
        if not self.is_acknowledged:
            self.is_acknowledged = True
            self.acknowledged_at = timezone.now()
            self.save()


class SafeZone(models.Model):
    """Predefined safe zones for users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='safe_zones')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.IntegerField(default=500, help_text="Radius in meters")
    
    # Settings
    is_active = models.BooleanField(default=True)
    send_entry_alert = models.BooleanField(default=True)
    send_exit_alert = models.BooleanField(default=True)
    
    # Time-based restrictions
    active_days = models.JSONField(
        default=list,
        help_text="Days when safe zone is active (0=Monday, 6=Sunday)"
    )
    active_start_time = models.TimeField(null=True, blank=True)
    active_end_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'safe_zones'
        verbose_name = 'Safe Zone'
        verbose_name_plural = 'Safe Zones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.phone}"
    
    def is_point_inside(self, latitude, longitude):
        """Check if a point is inside the safe zone"""
        from haversine import haversine
        
        zone_point = (self.latitude, self.longitude)
        check_point = (latitude, longitude)
        
        distance = haversine(zone_point, check_point, unit='m')
        
        return distance <= self.radius