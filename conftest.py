import secrets
from collections.abc import Callable
from typing import cast

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
def user_factory(db: None) -> Callable[..., User]:

    def _create(**kwargs: object) -> User:
        kwargs.setdefault("email", "shopper@example.com")

        password = cast(str, kwargs.pop("password", "correct-pass"))
        user_fields = cast(dict[str, str], kwargs)

        return User.objects.create_user(
            password=password,
            **user_fields,
        )

    return _create


@pytest.fixture
def authenticated_client(
    user_factory: Callable[..., User],
) -> tuple[APIClient, User]:

    password = secrets.token_urlsafe(16)
    user = user_factory(password=password)

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    return client, user
