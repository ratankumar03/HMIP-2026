from django.urls import path
from .views import (
    SubmitLocationView,
    MyLocationsView,
    UserLocationView,
    UserLocationHistoryView,
    LatestLocationView,
    LocationStatsView,
    LocationHistoryListView,
    DeleteLocationView,
    DeleteAllLocationsView,
)

app_name = 'location'

urlpatterns = [
    # Submit location
    path('submit/', SubmitLocationView.as_view(), name='submit-location'),

    # My locations
    path('my-locations/', MyLocationsView.as_view(), name='my-locations'),
    path('latest/', LatestLocationView.as_view(), name='latest-location'),
    path('stats/', LocationStatsView.as_view(), name='location-stats'),

    # User locations (with permission check)
    path('user/<uuid:user_id>/', UserLocationView.as_view(), name='user-location'),
    path('user/<uuid:user_id>/history/', UserLocationHistoryView.as_view(), name='user-location-history'),

    # Location history aggregates
    path('history/', LocationHistoryListView.as_view(), name='location-history'),

    # Delete operations
    path('delete/<uuid:location_id>/', DeleteLocationView.as_view(), name='delete-location'),
    path('delete-all/', DeleteAllLocationsView.as_view(), name='delete-all-locations'),
]