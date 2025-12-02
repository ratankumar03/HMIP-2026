# 🔗 Authentication URL Configuration
# File Location: backend/apps/authentication/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    RequestOTPView,
    VerifyOTPView,
    UserProfileView,
    ChangePasswordView,
    UserSessionsView,
    LogoutView,
    RegisterDeviceView,
)

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # OTP endpoints
    path('otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Session management
    path('sessions/', UserSessionsView.as_view(), name='sessions'),
    
    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Device registration
    path('device/register/', RegisterDeviceView.as_view(), name='register-device'),
]