from collections.abc import Callable

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import LoginEvent, User


def test_successful_login_records_an_event(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(
        email="shopper@example.com",
        password="correct-pass",
    )

    APIClient().post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "correct-pass"},
    )

    assert user.login_events.count() == 1


def test_failed_login_does_not_record_an_event(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(
        email="shopper@example.com",
        password="correct-pass",
    )

    APIClient().post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "wrong"},
    )

    assert user.login_events.count() == 0


def test_login_history_only_shows_the_requesting_users_own_events(
    user_factory: Callable[..., User],
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client
    other_user = user_factory(email="other@example.com")

    LoginEvent.objects.create(
        user=user,
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    LoginEvent.objects.create(
        user=other_user,
        ip_address="127.0.0.2",
        user_agent="pytest",
    )

    response = client.get("/api/v1/users/me/login-history/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["ip_address"] == "127.0.0.1"
