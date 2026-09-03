from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def test_default_storage_round_trips_a_file() -> None:

    name = default_storage.save("smoke-test.txt", ContentFile(b"hello, minio"))

    try:
        assert default_storage.exists(name)
        with default_storage.open(name) as f:
            assert f.read() == b"hello, minio"
    finally:
        default_storage.delete(name)
