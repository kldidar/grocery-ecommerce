"""URL routes for API version 1.

Every route in this module is implicitly prefixed with /api/v1/ (see the
`include()` call in config/urls.py). As applications gain real endpoints,
add one `path()` (or `include()`, for an application's own urls.py) per
line here — this module is the single place where v1 routes are aggregated.
"""

from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.common.views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-view"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("users/", include("apps.users.urls")),
]
