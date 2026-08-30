"""Smoke tests confirming the test environment itself is correctly configured.

These do not test application behaviour — they exist to fail loudly and
clearly if the settings module or the database connection is misconfigured,
rather than letting a real test fail with a confusing, unrelated error.
"""

import pytest
from django.conf import settings
from django.db import connection


def test_settings_module_is_the_development_one() -> None:
    """pytest-django must load config.settings.development, as configured."""
    assert settings.SETTINGS_MODULE == "config.settings.development"


@pytest.mark.django_db
def test_database_is_reachable() -> None:
    """A trivial query proves pytest-django successfully provisioned a test database."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)
