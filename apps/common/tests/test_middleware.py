import logging

import pytest
from rest_framework.test import APIClient


def test_request_id_is_echoed_in_the_response_header() -> None:
    response = APIClient().get("/api/health/")
    assert "X-Request-ID" in response.headers


def test_client_supplied_request_id_is_honoured() -> None:
    response = APIClient().get(
        "/api/health/",
        HTTP_X_REQUEST_ID="client-supplied-id",
    )
    assert response.headers["X-Request-ID"] == "client-supplied-id"


def test_request_logging_middleware_logs_the_request(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="apps.common.middleware"):
        APIClient().get("/api/health/")

    assert any(
        "GET" in record.message and "/api/health/" in record.message
        for record in caplog.records
    )
