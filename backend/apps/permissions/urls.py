from django.urls import path
from .views import (
    RequestLocationPermissionView,
    RespondToPermissionView,
    MyPermissionsView,
    PendingPermissionsView,
    ActivePermissionsView,
    RevokePermissionView,
    PermissionAlertsView,
    SafeZonesView,
    PermissionStatsView,
)

app_name = 'permissions'

urlpatterns = [
    path('request/', RequestLocationPermissionView.as_view(), name='request-permission'),
    path('respond/', RespondToPermissionView.as_view(), name='respond-permission'),
    path('my-permissions/', MyPermissionsView.as_view(), name='my-permissions'),
    path('pending/', PendingPermissionsView.as_view(), name='pending-permissions'),
    path('active/', ActivePermissionsView.as_view(), name='active-permissions'),
    path('revoke/<uuid:permission_id>/', RevokePermissionView.as_view(), name='revoke-permission'),
    path('alerts/', PermissionAlertsView.as_view(), name='permission-alerts'),
    path('safe-zones/', SafeZonesView.as_view(), name='safe-zones'),
    path('stats/', PermissionStatsView.as_view(), name='permission-stats'),
]
