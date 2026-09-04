import secrets

import pytest
from django.conf import LazySettings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    return client, user
