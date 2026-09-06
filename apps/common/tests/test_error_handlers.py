import json

from django.conf import LazySettings
from django.test import RequestFactory
from rest_framework.test import APIClient

from apps.common.views import handler500


def test_handler404_returns_the_common_json_shape_for_unmatched_urls(
    settings: LazySettings,
) -> None:
    settings.DEBUG = False

    response = APIClient().get("/api/v1/this-path-does-not-exist/")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_handler500_returns_the_common_json_shape() -> None:
    request = RequestFactory().get("/")
    response = handler500(request)
    data = json.loads(response.content)

    assert response.status_code == 500
    assert data["error"]["code"] == "internal_error"
    assert "request_id" in data["error"]["details"]
