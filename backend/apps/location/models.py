from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class LocationData(models.Model):
    """Store user location data"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    
    # Location coordinates
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(help_text="Accuracy in meters")
    
    # Movement data
    speed = models.FloatField(null=True, blank=True, help_text="Speed in km/h")
    heading = models.FloatField(null=True, blank=True, help_text="Direction in degrees")
    
    # Additional metadata
    battery_level = models.IntegerField(null=True, blank=True)
    is_moving = models.BooleanField(default=True)
    activity_type = models.CharField(
        max_length=20,
        choices=[
            ('stationary', 'Stationary'),
            ('walking', 'Walking'),
            ('running', 'Running'),
            ('cycling', 'Cycling'),
            ('driving', 'Driving'),
        ],
        null=True,
        blank=True
    )
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_data'
        verbose_name = 'Location Data'
        verbose_name_plural = 'Location Data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.user.phone} - {self.timestamp}"


class LocationHistory(models.Model):
    """Aggregated location history for analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_history')
    
    date = models.DateField(db_index=True)
    total_distance = models.FloatField(default=0, help_text="Total distance in km")
    avg_speed = models.FloatField(default=0, help_text="Average speed in km/h")
    max_speed = models.FloatField(default=0, help_text="Max speed in km/h")
    
    # Time spent in different activities
    time_stationary = models.IntegerField(default=0, help_text="Minutes")
    time_walking = models.IntegerField(default=0, help_text="Minutes")
    time_driving = models.IntegerField(default=0, help_text="Minutes")
    
    # Places visited
    unique_locations = models.IntegerField(default=0)
    frequent_locations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'location_history'
        verbose_name = 'Location History'
        verbose_name_plural = 'Location Histories'
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.phone} - {self.date}"