# 🔐 Authentication Views
# File Location: backend/apps/authentication/views.py

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
import logging

from .models import OTP, UserSession
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    OTPRequestSerializer,
    OTPVerificationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserSessionSerializer,
    DeviceRegistrationSerializer
)
from .utils import send_otp_sms

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    POST: Register a new user account
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate OTP for verification
            otp_code = str(random.randint(100000, 999999))
            otp = OTP.objects.create(
                user=user,
                phone=user.phone,
                otp_code=otp_code,
                purpose='verification',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send OTP via SMS
            send_otp_sms(user.phone, otp_code)
            
            return Response({
                'success': True,
                'message': 'Registration successful. OTP sent to your phone.',
                'user_id': user.id,
                'phone': user.phone
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    POST: Login user with phone and password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            if not user.is_verified:
                return Response({
                    'success': False,
                    'message': 'Please verify your phone number first.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Create user session
            session = UserSession.objects.create(
                user=user,
                token=access_token,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # Update last login
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class RequestOTPView(APIView):
    """
    POST: Request OTP for verification/login/permission
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            purpose = serializer.validated_data['purpose']
            
            # Check if user exists (for certain purposes)
            user = None
            if purpose in ['login', 'reset_password']:
                try:
                    user = User.objects.get(phone=phone)
                except User.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'User with this phone number not found.'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            
            # Delete old unused OTPs
            OTP.objects.filter(
                phone=phone,
                purpose=purpose,
                is_used=False
            ).delete()
            
            # Create new OTP
            otp = OTP.objects.create(
                user=user,
                phone=phone,
                otp_code=otp_code,
                purpose=purpose,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send OTP via SMS
            send_otp_sms(phone, otp_code)
            
            logger.info(f"OTP sent to {phone} for purpose: {purpose}")
            
            return Response({
                'success': True,
                'message': f'OTP sent successfully to {phone}',
                'expires_in': 600  # 10 minutes in seconds
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    POST: Verify OTP code
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp_code = serializer.validated_data['otp_code']
            purpose = serializer.validated_data['purpose']
            
            try:
                otp = OTP.objects.get(
                    phone=phone,
                    otp_code=otp_code,
                    purpose=purpose,
                    is_used=False
                )
                
                if not otp.is_valid():
                    if otp.expires_at < timezone.now():
                        return Response({
                            'success': False,
                            'message': 'OTP has expired. Please request a new one.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        otp.attempts += 1
                        otp.save()
                        return Response({
                            'success': False,
                            'message': 'Too many attempts. Please request a new OTP.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark OTP as used
                otp.is_used = True
                otp.save()
                
                # Handle different purposes
                if purpose == 'verification' and otp.user:
                    otp.user.is_verified = True
                    otp.user.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Phone verified successfully'
                    }, status=status.HTTP_200_OK)
                
                elif purpose == 'login':
                    user = otp.user
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                    
                    return Response({
                        'success': True,
                        'message': 'Login successful',
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                
                else:
                    return Response({
                        'success': True,
                        'message': 'OTP verified successfully'
                    }, status=status.HTTP_200_OK)
                
            except OTP.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Invalid OTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET: Get current user profile
    PUT/PATCH: Update user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """
    POST: Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'success': False,
                    'message': 'Incorrect old password'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"Password changed for user {user.phone}")
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserSessionsView(generics.ListAPIView):
    """
    GET: List all active sessions for current user
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSessionSerializer
    
    def get_queryset(self):
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')


class LogoutView(APIView):
    """
    POST: Logout user and invalidate session
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Get the token from header
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]
            
            # Deactivate session
            UserSession.objects.filter(
                user=request.user,
                token=token,
                is_active=True
            ).update(is_active=False)
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterDeviceView(APIView):
    """
    POST: Register device for push notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = DeviceRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            user.device_id = serializer.validated_data['device_id']
            user.fcm_token = serializer.validated_data['fcm_token']
            user.save()
            
            return Response({
                'success': True,
                'message': 'Device registered successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)