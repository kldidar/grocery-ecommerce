import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.common.validators import validate_image_file


def _make_image_file(content_type: str = "image/jpeg") -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile("avatar.jpg", buffer.read(), content_type=content_type)


def test_accepts_a_genuine_small_jpeg() -> None:

    validate_image_file(_make_image_file())


def test_rejects_a_file_pretending_to_be_an_image() -> None:

    fake = SimpleUploadedFile(
        "not-really.jpg",
        b"this is definitely not image data",
        content_type="image/jpeg",
    )
    with pytest.raises(ValidationError):
        validate_image_file(fake)


def test_rejects_a_disallowed_content_type() -> None:

    file = SimpleUploadedFile(
        "script.svg", b"<svg></svg>", content_type="image/svg+xml"
    )
    with pytest.raises(ValidationError):
        validate_image_file(file)


def test_rejects_a_file_larger_than_the_limit() -> None:

    oversized = _make_image_file()
    oversized.size = 6 * 1024 * 1024  # simulate 6 MB without allocating it
    with pytest.raises(ValidationError):
        validate_image_file(oversized)
