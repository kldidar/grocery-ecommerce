from dataclasses import dataclass
from typing import Any

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
