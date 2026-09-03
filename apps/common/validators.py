from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_file(file: UploadedFile[bytes]) -> None:

    if file.size is not None and file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            f"Image must not exceed {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError("Unsupported image type. Allowed: JPEG, PNG, WEBP.")

    try:
        with Image.open(file) as image:
            image.verify()

    except UnidentifiedImageError as exc:
        raise ValidationError("The uploaded file is not a valid image.") from exc

    finally:
        file.seek(0)
