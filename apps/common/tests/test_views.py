from rest_framework import status
from rest_framework.test import APIClient


def test_health_check_returns_ok() -> None:

    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok"}


def test_health_check_does_not_require_authentication() -> None:

    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
