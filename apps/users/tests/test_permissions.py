from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest
from rest_framework.permissions import IsAdminUser
from rest_framework.test import APIRequestFactory

from apps.users.models import User
from apps.users.permissions import IsOwnerOrReadOnly


@dataclass
class _FakeRequest:
    method: str
    user: Any


@dataclass
class _FakeOwnedObject:
    user: Any


def test_safe_methods_are_allowed_regardless_of_ownership() -> None:

    permission = IsOwnerOrReadOnly()
    owner, other_user = object(), object()
    request = _FakeRequest(method="GET", user=other_user)
    obj = _FakeOwnedObject(user=owner)
    view = None  # unused by this permission's logic
    assert permission.has_object_permission(request, view, obj) is True  # type: ignore[arg-type]


def test_write_methods_are_allowed_only_for_the_owner() -> None:

    permission = IsOwnerOrReadOnly()
    owner, other_user = object(), object()
    obj = _FakeOwnedObject(user=owner)
    view = None  # unused by this permission's logic

    owner_request = _FakeRequest(method="PATCH", user=owner)
    other_request = _FakeRequest(method="PATCH", user=other_user)

    assert permission.has_object_permission(owner_request, view, obj) is True  # type: ignore[arg-type]
    assert permission.has_object_permission(other_request, view, obj) is False  # type: ignore[arg-type]


@pytest.mark.django_db
def test_is_admin_user_correctly_reads_custom_user_is_staff(
    user_factory: Callable[..., User],
) -> None:
    """Verify DRF's IsAdminUser works with the custom User model."""
    staff_user = user_factory(
        email="staff@example.com",
        is_staff=True,
    )
    regular_user = user_factory(
        email="regular@example.com",
        is_staff=False,
    )

    factory = APIRequestFactory()
    permission = IsAdminUser()

    staff_request = factory.get("/")
    staff_request.user = staff_user

    regular_request = factory.get("/")
    regular_request.user = regular_user

    assert permission.has_permission(staff_request, view=None) is True  # type: ignore[arg-type]
    assert permission.has_permission(regular_request, view=None) is False  # type: ignore[arg-type]
