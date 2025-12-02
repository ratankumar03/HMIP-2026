# 📋 Celery Tasks for Permissions App
# File Location: backend/apps/permissions/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_permission_request_notification(self, permission_id, user_email):
    """
    Send notification when a permission request is created
    """
    try:
        # TODO: Implement actual notification logic
        logger.info(f"Sending permission request notification for permission {permission_id} to {user_email}")

        # Example email notification
        send_mail(
            subject='New Permission Request',
            message=f'You have a new permission request (ID: {permission_id})',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        return f"Notification sent successfully for permission {permission_id}"

    except Exception as exc:
        logger.error(f"Failed to send notification: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_expired_permissions():
    """
    Periodic task to check and update expired permissions
    """
    try:
        from .models import Permission
        from django.utils import timezone

        # Find and update expired permissions
        expired_count = Permission.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        ).update(status='expired')

        logger.info(f"Marked {expired_count} permissions as expired")
        return f"Processed {expired_count} expired permissions"

    except Exception as exc:
        logger.error(f"Failed to check expired permissions: {exc}")
        raise


@shared_task
def send_permission_expiry_reminder(permission_id):
    """
    Send reminder before permission expires
    """
    try:
        # TODO: Implement expiry reminder logic
        logger.info(f"Sending expiry reminder for permission {permission_id}")
        return f"Reminder sent for permission {permission_id}"

    except Exception as exc:
        logger.error(f"Failed to send expiry reminder: {exc}")
        raise
