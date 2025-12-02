# 🔌 ASGI Configuration for WebSockets
# File Location: backend/hmip_backend/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmip_backend.settings')

# Initialize Django ASGI application early to ensure AppRegistry is populated
django_asgi_app = get_asgi_application()

# Import WebSocket routing after Django initialization
from apps.location.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP requests
    "http": django_asgi_app,
    
    # WebSocket requests
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})