import uuid

from apps.common.models import BaseModel, TimestampMixin, UUIDMixin


def test_uuid_mixin_defines_a_uuid_primary_key() -> None:

    field = UUIDMixin._meta.get_field("id")
    assert field.primary_key is True
    assert field.editable is False
    assert field.default is uuid.uuid4


def test_timestamp_mixin_defines_created_and_updated_fields() -> None:

    created_at = TimestampMixin._meta.get_field("created_at")
    updated_at = TimestampMixin._meta.get_field("updated_at")
    assert created_at.auto_now_add is True
    assert updated_at.auto_now is True


def test_base_model_combines_both_mixins() -> None:

    field_names = {field.name for field in BaseModel._meta.get_fields()}
    assert {"id", "created_at", "updated_at"}.issubset(field_names)


def test_all_three_bases_are_abstract() -> None:

    assert UUIDMixin._meta.abstract is True
    assert TimestampMixin._meta.abstract is True
    assert BaseModel._meta.abstract is True
