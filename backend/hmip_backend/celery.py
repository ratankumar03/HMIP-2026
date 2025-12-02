# 📋 Celery Configuration
# File Location: backend/hmip_backend/celery.py

import os
import sys
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmip_backend.settings')

app = Celery('hmip_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for Periodic Tasks
app.conf.beat_schedule = {
    # Check expired permissions every hour
    'check-expired-permissions': {
        'task': 'apps.permissions.tasks.check_expired_permissions',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour
    },
    
    # Clean old location data every day at 2 AM
    'clean-old-location-data': {
        'task': 'apps.location.tasks.clean_old_location_data',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    
    # Update AI predictions every 30 minutes
    'update-ai-predictions': {
        'task': 'apps.ai_engine.tasks.update_predictions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    
    # Send pending notifications every 5 minutes
    'send-pending-notifications': {
        'task': 'apps.notifications.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    
    # Generate daily analytics reports
    'generate-daily-reports': {
        'task': 'apps.ai_engine.tasks.generate_daily_analytics',
        'schedule': crontab(minute=0, hour=0),  # Daily at midnight
    },
}

# Celery Configuration
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Windows-specific configuration
if sys.platform == 'win32':
    # Use solo pool on Windows to avoid multiprocessing issues
    app.conf.worker_pool = 'solo'
    print("Running on Windows - using 'solo' pool for Celery worker")

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')