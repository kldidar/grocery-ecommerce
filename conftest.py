import secrets

import pytest
from django.conf import LazySettings
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture(autouse=True)
def _celery_eager(settings: LazySettings) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def authenticated_client(db: None) -> tuple[APIClient, User]:
    password = secrets.token_urlsafe(16)

    user = User.objects.create_user(
        email="shopper@example.com",
        password=password,
    )

    client = APIClient()

    tokens = client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": password},
    )

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {tokens.data['access']}",
    )

    return client, user
