# 🏠 Home Page View
# File Location: backend/hmip_backend/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def api_home(request):
    """
    API Home - Welcome page with available endpoints
    """
    return JsonResponse({
        'message': 'Welcome to HMIP-2026 API',
        'description': 'AI-Powered Real-Time Location Tracking & Mobility Intelligence Platform',
        'version': 'v1.0.0',
        'status': 'running',
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'api_docs': '/api/docs/'
        },
        'endpoints': {
            'authentication': '/api/auth/',
            'permissions': '/api/permissions/',
            'location': '/api/location/',
            'ai_engine': '/api/ai/',
            'notifications': '/api/notifications/',
            'admin': '/admin/'
        },
        'features': [
            'Real-time Location Tracking',
            'WebSocket Support',
            'AI-Powered Anomaly Detection',
            'Permission-based Tracking',
            'Geofencing & Safe Zones',
            'Multi-channel Notifications'
        ],
        'database': {
            'django_models': 'SQLite (User, Auth, Sessions)',
            'application_data': 'MongoDB (Locations, Permissions, Notifications)'
        }
    })


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    from hmip_backend.mongodb import mongodb
    from django.db import connection

    health_status = {
        'status': 'healthy',
        'services': {}
    }

    # Check Django DB
    try:
        connection.ensure_connection()
        health_status['services']['django_db'] = 'connected'
    except Exception as e:
        health_status['services']['django_db'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'

    # Check MongoDB
    try:
        mongodb.client.server_info()
        health_status['services']['mongodb'] = f'connected ({mongodb.db.name})'
    except Exception as e:
        health_status['services']['mongodb'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'

    # Check Redis (optional)
    try:
        from redis import Redis
        from django.conf import settings
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
        )
        redis_client.ping()
        health_status['services']['redis'] = 'connected'
    except Exception as e:
        health_status['services']['redis'] = f'disconnected: {str(e)}'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)
