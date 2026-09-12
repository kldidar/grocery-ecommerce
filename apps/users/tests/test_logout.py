from collections.abc import Callable

import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.mark.django_db
def test_logout_blacklists_the_refresh_token(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(
        email="real@example.com",
        password="correct-pass",
    )

    cache.clear()

    client = APIClient()
    tokens = client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "correct-pass"},
    )

    assert tokens.status_code == status.HTTP_200_OK
    refresh = tokens.data["refresh"]

    logout_response = client.post(
        "/api/v1/auth/logout/",
        {"refresh": refresh},
    )

    assert logout_response.status_code == status.HTTP_204_NO_CONTENT

    reuse_attempt = client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": refresh},
    )

    assert reuse_attempt.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_logout_with_an_already_blacklisted_token_is_rejected(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(
        email="real@example.com",
        password="correct-pass",
    )

    cache.clear()

    client = APIClient()
    tokens = client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "correct-pass"},
    )

    assert tokens.status_code == status.HTTP_200_OK
    refresh = tokens.data["refresh"]

    first_attempt = client.post(
        "/api/v1/auth/logout/",
        {"refresh": refresh},
    )
    assert first_attempt.status_code == status.HTTP_204_NO_CONTENT

    second_attempt = client.post(
        "/api/v1/auth/logout/",
        {"refresh": refresh},
    )

    assert second_attempt.status_code == status.HTTP_400_BAD_REQUEST
