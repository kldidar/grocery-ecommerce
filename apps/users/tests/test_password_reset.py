from collections.abc import Callable

import pytest
from django.core import mail
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
