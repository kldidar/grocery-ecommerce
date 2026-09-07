from collections.abc import Callable

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


def test_registration_creates_an_active_unverified_user(db: None) -> None:
    response = APIClient().post(
        "/api/v1/auth/register/",
        {"email": "new@example.com", "password": "a-strong-passw0rd"},
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = User.objects.get(email="new@example.com")

    assert user.is_active is True
    assert user.check_password("a-strong-passw0rd") is True


def test_registration_rejects_a_weak_password(db: None) -> None:
    response = APIClient().post(
        "/api/v1/auth/register/",
        {"email": "new@example.com", "password": "123"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_registration_rejects_a_duplicate_email(
    user_factory: Callable[..., User],
) -> None:
    user_factory(email="taken@example.com")

    response = APIClient().post(
        "/api/v1/auth/register/",
        {"email": "taken@example.com", "password": "a-strong-passw0rd"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
