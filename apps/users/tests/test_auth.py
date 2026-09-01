import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def user(db: None) -> User:
    return User.objects.create_user(
        email="shopper@example.com",
        password="correct-pass",
    )


def test_obtain_token_pair_with_valid_credentials(user: User) -> None:
    response = APIClient().post(
        "/api/v1/auth/token/",
        {
            "email": "shopper@example.com",
            "password": "correct-pass",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


def test_obtain_token_pair_with_wrong_password_is_rejected(
    user: User,
) -> None:
    response = APIClient().post(
        "/api/v1/auth/token/",
        {
            "email": "shopper@example.com",
            "password": "wrong-pass",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_issues_a_new_access_token(user: User) -> None:
    client = APIClient()

    obtained = client.post(
        "/api/v1/auth/token/",
        {
            "email": "shopper@example.com",
            "password": "correct-pass",
        },
    )

    refreshed = client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": obtained.data["refresh"]},
    )

    assert refreshed.status_code == status.HTTP_200_OK
    assert "access" in refreshed.data
