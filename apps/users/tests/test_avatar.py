import io

from django.core.files.storage import default_storage
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


def _jpeg_upload(name: str = "avatar.jpg") -> io.BytesIO:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, format="JPEG")
    buffer.seek(0)
    buffer.name = name
    return buffer


def test_uploading_an_avatar_succeeds(
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client

    response = client.patch(
        "/api/v1/users/me/",
        {"avatar": _jpeg_upload()},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["avatar"] is not None

    user.refresh_from_db()

    assert user.avatar.name is not None
    assert user.avatar.name.startswith("avatars/")

    user.avatar.delete(save=False)


def test_replacing_an_avatar_deletes_the_old_file_from_storage(
    authenticated_client: tuple[APIClient, User],
) -> None:
    client, user = authenticated_client

    client.patch(
        "/api/v1/users/me/",
        {"avatar": _jpeg_upload("first.jpg")},
        format="multipart",
    )

    user.refresh_from_db()

    assert user.avatar.name is not None
    old_name = user.avatar.name

    client.patch(
        "/api/v1/users/me/",
        {"avatar": _jpeg_upload("second.jpg")},
        format="multipart",
    )

    assert not default_storage.exists(old_name)

    user.refresh_from_db()
    user.avatar.delete(save=False)
