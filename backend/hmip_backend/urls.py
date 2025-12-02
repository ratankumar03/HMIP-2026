# 🌐 Main URL Configuration
# File Location: backend/hmip_backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import api_home, health_check

# Swagger API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="HMIP-2026 API",
        default_version='v1',
        description="AI-Powered Real-Time Location Tracking & Mobility Intelligence Platform API",
        terms_of_service="https://www.hmip.com/terms/",
        contact=openapi.Contact(email="contact@hmip.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Home & Health Check
    path('', api_home, name='api-home'),
    path('health/', health_check, name='health-check'),

    # Admin Panel
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),

    # API Endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/permissions/', include('apps.permissions.urls')),
    path('api/location/', include('apps.location.urls')),
    path('api/ai/', include('apps.ai_engine.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = "HMIP-2026 Administration"
admin.site.site_title = "HMIP-2026 Admin Portal"
admin.site.index_title = "Welcome to HMIP-2026 Management"