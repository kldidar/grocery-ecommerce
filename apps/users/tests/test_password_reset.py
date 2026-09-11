from collections.abc import Callable

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.mark.django_db
def test_request_returns_the_same_response_for_an_unknown_email() -> None:
    response = APIClient().post(
        "/api/v1/auth/password-reset/",
        {"email": "nobody@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_request_sends_an_email_only_for_a_registered_user(
    user_factory: Callable[..., User],
) -> None:
    user_factory(email="real@example.com")

    mail.outbox.clear()

    APIClient().post(
        "/api/v1/auth/password-reset/",
        {"email": "real@example.com"},
    )

    assert len(mail.outbox) == 1

    mail.outbox.clear()

    APIClient().post(
        "/api/v1/auth/password-reset/",
        {"email": "nobody@example.com"},
    )

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_confirm_with_a_valid_token_changes_the_password(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="real@example.com", password="old-passw0rd")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = APIClient().post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "a-new-strong-passw0rd"},
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("a-new-strong-passw0rd") is True


@pytest.mark.django_db
def test_confirm_rejects_a_password_too_similar_to_the_email(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="ada.lovelace@example.com", password="old-passw0rd")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = APIClient().post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "ada.lovelace@example.com"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_confirm_rejects_a_token_that_was_already_used(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="real@example.com", password="old-passw0rd")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    client = APIClient()

    client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "a-new-strong-passw0rd"},
    )
    second_attempt = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "yet-another-passw0rd"},
    )

    assert second_attempt.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_confirm_blacklists_refresh_tokens_issued_before_the_reset(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(
        email="real@example.com",
        password="old-passw0rd",
    )

    cache.clear()

    client = APIClient()
    tokens = client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "old-passw0rd"},
    )

    assert tokens.status_code == status.HTTP_200_OK
    old_refresh_token = tokens.data["refresh"]

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {
            "uid": uid,
            "token": token,
            "new_password": "a-new-strong-passw0rd",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    refresh_attempt = client.post(
        "/api/v1/auth/token/refresh/",
        {"refresh": old_refresh_token},
    )

    assert refresh_attempt.status_code == status.HTTP_401_UNAUTHORIZED
