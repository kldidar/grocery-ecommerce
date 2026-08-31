"""URL routes for API version 1.

Every route in this module is implicitly prefixed with /api/v1/ (see the
`include()` call in config/urls.py). As applications gain real endpoints,
add one `path()` (or `include()`, for an application's own urls.py) per
line here — this module is the single place where v1 routes are aggregated.
"""

from django.urls import path

from apps.common.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
