# 🛠️ Authentication Utility Functions
# File Location: backend/apps/authentication/utils.py

from django.conf import settings
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


def send_otp_sms(phone_number, otp_code):
    """
    Send OTP via SMS using Twilio
    
    Args:
        phone_number (str): Phone number to send OTP to
        otp_code (str): 6-digit OTP code
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    try:
        # Format phone number with country code if not present
        if not phone_number.startswith('+'):
            phone_number = f'+91{phone_number}'  # Default to India, change as needed
        
        # Initialize Twilio client
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Send SMS
            message = client.messages.create(
                body=f'Your HMIP-2026 verification code is: {otp_code}. Valid for 10 minutes. Do not share this code.',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"OTP SMS sent to {phone_number}. SID: {message.sid}")
            return True
        else:
            # For development - just log the OTP
            logger.warning(f"Twilio not configured. OTP for {phone_number}: {otp_code}")
            print(f"\n{'='*50}")
            print(f"🔐 OTP for {phone_number}: {otp_code}")
            print(f"{'='*50}\n")
            return True
    
    except Exception as e:
        logger.error(f"Error sending OTP to {phone_number}: {str(e)}")
        # For development, still log the OTP
        print(f"\n{'='*50}")
        print(f"🔐 OTP for {phone_number}: {otp_code}")
        print(f"{'='*50}\n")
        return False


def format_phone_number(phone):
    """
    Format phone number to standard format
    
    Args:
        phone (str): Phone number to format
    
    Returns:
        str: Formatted phone number
    """
    # Remove all non-digit characters
    import re
    phone = re.sub(r'\D', '', phone)
    
    # Add country code if not present
    if len(phone) == 10:
        phone = f'91{phone}'  # Add India country code
    
    return phone


def validate_phone_number(phone):
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    phone = re.sub(r'\D', '', phone)
    
    # Check if phone number is between 10-15 digits
    if 10 <= len(phone) <= 15:
        return True
    
    return False


def generate_user_token(user):
    """
    Generate JWT token for user
    
    Args:
        user (User): User instance
    
    Returns:
        dict: Dictionary containing access and refresh tokens
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def get_client_ip(request):
    """
    Get client IP address from request
    
    Args:
        request: Django request object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def get_user_agent(request):
    """
    Get user agent from request
    
    Args:
        request: Django request object
    
    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def parse_device_info(user_agent):
    """
    Parse device information from user agent
    
    Args:
        user_agent (str): User agent string
    
    Returns:
        dict: Device information
    """
    import re
    
    device_info = {
        'platform': 'Unknown',
        'browser': 'Unknown',
        'device_type': 'Unknown'
    }
    
    # Detect platform
    if 'Windows' in user_agent:
        device_info['platform'] = 'Windows'
    elif 'Mac' in user_agent:
        device_info['platform'] = 'macOS'
    elif 'Linux' in user_agent:
        device_info['platform'] = 'Linux'
    elif 'Android' in user_agent:
        device_info['platform'] = 'Android'
        device_info['device_type'] = 'Mobile'
    elif 'iOS' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent:
        device_info['platform'] = 'iOS'
        device_info['device_type'] = 'Mobile' if 'iPhone' in user_agent else 'Tablet'
    
    # Detect browser
    if 'Chrome' in user_agent and 'Edge' not in user_agent:
        device_info['browser'] = 'Chrome'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        device_info['browser'] = 'Safari'
    elif 'Firefox' in user_agent:
        device_info['browser'] = 'Firefox'
    elif 'Edge' in user_agent:
        device_info['browser'] = 'Edge'
    
    return device_info