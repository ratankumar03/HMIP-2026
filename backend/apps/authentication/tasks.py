# 📋 Celery Tasks for Authentication App
# File Location: backend/apps/authentication/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_otp_email(self, user_email, otp_code):
    """
    Send OTP code via email
    """
    try:
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP code is: {otp_code}\n\nThis code will expire in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"OTP email sent to {user_email}")
        return f"OTP sent to {user_email}"

    except Exception as exc:
        logger.error(f"Failed to send OTP email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_email, user_name):
    """
    Send welcome email to new users
    """
    try:
        send_mail(
            subject='Welcome to HMIP!',
            message=f'Hello {user_name},\n\nWelcome to HMIP - Human Missing Identification Platform.\n\nThank you for joining us!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user_email}")
        return f"Welcome email sent to {user_email}"

    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_email, reset_link):
    """
    Send password reset email
    """
    try:
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 1 hour.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        logger.info(f"Password reset email sent to {user_email}")
        return f"Password reset email sent to {user_email}"

    except Exception as exc:
        logger.error(f"Failed to send password reset email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_otps():
    """
    Periodic task to clean up expired OTP codes
    """
    try:
        from .models import OTP
        from django.utils import timezone

        # Delete expired OTPs
        deleted_count = OTP.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]

        logger.info(f"Cleaned up {deleted_count} expired OTPs")
        return f"Cleaned {deleted_count} expired OTPs"

    except Exception as exc:
        logger.error(f"Failed to cleanup expired OTPs: {exc}")
        raise
