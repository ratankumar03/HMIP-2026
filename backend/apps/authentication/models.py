# 👤 User Authentication Models
# File Location: backend/apps/authentication/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular user"""
        if not phone:
            raise ValueError('Users must have a phone number')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with phone number authentication"""
    
    ROLE_CHOICES = (
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Profile information
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Location preferences
    allow_location_tracking = models.BooleanField(default=False)
    share_location_by_default = models.BooleanField(default=False)
    
    # Device information
    device_id = models.CharField(max_length=255, blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)  # Firebase Cloud Messaging
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.phone} - {self.full_name or 'No Name'}"
    
    def get_full_name(self):
        return self.full_name or self.phone
    
    def get_short_name(self):
        return self.phone


class OTP(models.Model):
    """OTP model for phone verification"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    phone = models.CharField(max_length=15, db_index=True)
    otp_code = models.CharField(max_length=6)
    
    purpose = models.CharField(max_length=50, choices=[
        ('verification', 'Phone Verification'),
        ('login', 'Login'),
        ('permission', 'Location Permission'),
        ('reset_password', 'Password Reset'),
    ])
    
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'otp_code']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.phone} - {self.purpose}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and self.expires_at > timezone.now() and self.attempts < 3


class UserSession(models.Model):
    """Track user sessions for security"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    
    token = models.CharField(max_length=500, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.user.phone}"
    
    def is_valid(self):
        """Check if session is still valid"""
        return self.is_active and self.expires_at > timezone.now()