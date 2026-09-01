import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
def test_create_user_sets_expected_defaults() -> None:
    user = User.objects.create_user(email="shopper@example.com", password="s3cret-pass")
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True
    assert user.check_password("s3cret-pass") is True
    assert user.password != "s3cret-pass"


@pytest.mark.django_db
def test_create_user_normalizes_email_domain() -> None:
    user = User.objects.create_user(email="Shopper@EXAMPLE.com", password="s3cret-pass")
    assert user.email == "Shopper@example.com"


@pytest.mark.django_db
def test_create_user_without_email_raises() -> None:
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="s3cret-pass")


@pytest.mark.django_db
def test_create_superuser_sets_expected_flags() -> None:
    admin = User.objects.create_superuser(
        email="admin@example.com", password="s3cret-pass"
    )
    assert admin.is_staff is True
    assert admin.is_superuser is True


@pytest.mark.django_db
def test_create_superuser_rejects_is_staff_false() -> None:
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="admin@example.com", password="s3cret-pass", is_staff=False
        )


@pytest.mark.django_db
def test_email_is_unique() -> None:
    User.objects.create_user(email="shopper@example.com", password="s3cret-pass")
    with pytest.raises(IntegrityError):
        User.objects.create_user(email="shopper@example.com", password="another-pass")


def test_username_field_is_email() -> None:
    assert User.USERNAME_FIELD == "email"
    assert User.REQUIRED_FIELDS == []


def test_user_string_representation_is_email() -> None:
    assert str(User(email="shopper@example.com")) == "shopper@example.com"
