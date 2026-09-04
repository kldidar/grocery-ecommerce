from typing import cast

from django.conf import LazySettings
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

TEST_CACHE_SETTINGS = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "throttle-tests",
    }
}


@override_settings(CACHES=TEST_CACHE_SETTINGS)
def test_health_check_is_never_throttled(settings: LazySettings) -> None:
    throttle_rates = cast(
        dict[str, str],
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
    )
    throttle_rates["anon"] = "1/hour"

    client = APIClient()

    for _ in range(5):
        response = client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK


@override_settings(CACHES=TEST_CACHE_SETTINGS)
def test_login_attempts_are_throttled_beyond_the_configured_rate(
    settings: LazySettings,
) -> None:
    throttle_rates = cast(
        dict[str, str],
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
    )
    throttle_rates["login"] = "2/minute"

    client = APIClient()

    credentials = {
        "email": "nobody@example.com",
        "password": "wrong",
    }

    for _ in range(2):
        response = client.post("/api/v1/auth/token/", credentials)
        assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    throttled = client.post("/api/v1/auth/token/", credentials)

    assert throttled.status_code == status.HTTP_429_TOO_MANY_REQUESTS
