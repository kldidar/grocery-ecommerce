import pytest
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIClient

from apps.common.exceptions import custom_exception_handler


def test_handler_wraps_a_simple_detail_exception() -> None:

    response = custom_exception_handler(NotFound(), context={})
    assert response is not None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"]["code"] == "not_found"
    assert response.data["error"]["details"] is None


def test_handler_places_field_errors_under_details() -> None:

    response = custom_exception_handler(
        ValidationError({"email": ["This field is required."]}), context={}
    )
    assert response is not None
    assert response.data["error"]["code"] == "validation_error"
    assert response.data["error"]["details"] == {"email": ["This field is required."]}


def test_handler_returns_a_response_for_exceptions_drf_does_not_recognize() -> None:

    response = custom_exception_handler(RuntimeError("boom"), context={})
    assert response is not None
    assert response.status_code == 500
    assert response.data["error"]["code"] == "internal_error"
    assert "request_id" in response.data["error"]["details"]


def test_authentication_error_uses_the_common_shape_end_to_end() -> None:

    response = APIClient().get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_validation_error_end_to_end() -> None:

    response = APIClient().post("/api/v1/auth/token/", {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data["error"]["details"]
