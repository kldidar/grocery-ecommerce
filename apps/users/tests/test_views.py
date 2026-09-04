import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


@pytest.fixture
def user(db: None) -> User:

    return User.objects.create_user(
        email="shopper@example.com", password="correct-pass", first_name="Ada"
    )


def _authenticated_client(user: User) -> APIClient:
    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    return client


def test_me_requires_authentication() -> None:

    response = APIClient().get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_returns_the_authenticated_users_own_profile(user: User) -> None:

    response = _authenticated_client(user).get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == "shopper@example.com"
    assert response.data["first_name"] == "Ada"


def test_me_allows_updating_writable_fields(user: User) -> None:

    response = _authenticated_client(user).patch(
        "/api/v1/users/me/", {"last_name": "Lovelace"}
    )
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.last_name == "Lovelace"


def test_me_ignores_attempts_to_change_email(user: User) -> None:

    _authenticated_client(user).patch(
        "/api/v1/users/me/", {"email": "someone-else@example.com"}
    )
    user.refresh_from_db()
    assert user.email == "shopper@example.com"
