from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


def test_me_requires_authentication() -> None:
    response = APIClient().get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_returns_the_authenticated_users_own_profile(
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client

    response = client.get("/api/v1/users/me/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


def test_me_allows_updating_writable_fields(
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client

    response = client.patch(
        "/api/v1/users/me/",
        {"last_name": "Lovelace"},
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.last_name == "Lovelace"


def test_me_ignores_attempts_to_change_email(
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client

    response = client.patch(
        "/api/v1/users/me/",
        {"email": "someone-else@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.email == "shopper@example.com"
