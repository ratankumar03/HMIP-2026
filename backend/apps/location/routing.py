# 🔌 WebSocket URL Routing for Location App
# File Location: backend/apps/location/routing.py

from django.urls import re_path
from . import consumers

# WebSocket URL patterns for location tracking
websocket_urlpatterns = [
    re_path(r'ws/location/track/$', consumers.LocationTrackingConsumer.as_asgi()),
    re_path(r'ws/location/updates/(?P<user_id>\w+)/$', consumers.LocationUpdatesConsumer.as_asgi()),
]