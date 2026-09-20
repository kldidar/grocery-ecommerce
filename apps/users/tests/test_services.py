from collections.abc import Callable

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.services import blacklist_all_tokens_for


def _issue_outstanding_tokens(user: User, count: int) -> None:
    for _ in range(count):
        RefreshToken.for_user(user)


@pytest.mark.django_db
def test_blacklist_all_tokens_for_blacklists_every_outstanding_token(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="shopper@example.com")
    _issue_outstanding_tokens(user, 3)

    blacklist_all_tokens_for(user)

    outstanding = OutstandingToken.objects.filter(user=user)
    assert outstanding.count() == 3
    assert BlacklistedToken.objects.filter(token__in=outstanding).count() == 3


@pytest.mark.django_db
def test_blacklist_all_tokens_for_does_not_scale_queries_with_token_count(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="shopper@example.com")
    _issue_outstanding_tokens(user, 5)

    with CaptureQueriesContext(connection) as captured:
        blacklist_all_tokens_for(user)

    # Before the fix this was 1 + N*(1..2) queries (a get_or_create per
    # token). With bulk_create it is one SELECT plus one bulk INSERT,
    # regardless of how many tokens exist.
    assert len(captured) <= 2


@pytest.mark.django_db
def test_blacklist_all_tokens_for_is_idempotent_for_already_blacklisted_tokens(
    user_factory: Callable[..., User],
) -> None:
    user = user_factory(email="shopper@example.com")
    _issue_outstanding_tokens(user, 2)

    blacklist_all_tokens_for(user)
    blacklist_all_tokens_for(user)

    outstanding = OutstandingToken.objects.filter(user=user)
    assert BlacklistedToken.objects.filter(token__in=outstanding).count() == 2
