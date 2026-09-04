from typing import cast

from django.conf import settings


def test_x_frame_options_is_deny() -> None:
    assert settings.X_FRAME_OPTIONS == "DENY"


def test_content_type_nosniff_is_enabled() -> None:
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True


def test_cors_is_closed_by_default() -> None:
    assert settings.CORS_ALLOWED_ORIGINS == []


def test_login_has_a_dedicated_stricter_throttle_rate() -> None:
    rates = cast(
        dict[str, str],
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
    )

    assert "login" in rates
    assert "anon" in rates
    assert "user" in rates


def test_secret_key_meets_the_minimum_length() -> None:
    assert len(settings.SECRET_KEY) >= 32
