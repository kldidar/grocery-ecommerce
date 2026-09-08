from collections.abc import Callable

from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.users.tokens import email_verification_token


def test_registration_sends_a_verification_email(db: None) -> None:
    response = APIClient().post(
        "/api/v1/auth/register/",
        {
            "email": "new@example.com",
            "password": "a-strong-passw0rd",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(mail.outbox) == 1
    assert "Confirm your email" in mail.outbox[0].subject


def test_verify_email_with_a_valid_token_marks_the_user_verified(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="new@example.com")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    response = APIClient().post(
        "/api/v1/auth/verify-email/",
        {
            "uid": uid,
            "token": token,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.is_verified is True


def test_verify_email_with_an_invalid_token_is_rejected(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="new@example.com")

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    response = APIClient().post(
        "/api/v1/auth/verify-email/",
        {
            "uid": uid,
            "token": "not-a-real-token",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
