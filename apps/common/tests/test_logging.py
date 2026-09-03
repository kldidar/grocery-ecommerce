import json
import logging
from typing import Protocol, cast

from pythonjsonlogger.json import JsonFormatter

from apps.common.logging import RequestIDFilter, request_id_var


class RequestIDLogRecord(Protocol):
    request_id: str


def _make_record() -> logging.LogRecord:
    return logging.LogRecord(
        name="apps.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )


def test_request_id_filter_injects_the_current_context_value() -> None:
    token = request_id_var.set("test-request-id")
    try:
        record = _make_record()
        assert RequestIDFilter().filter(record) is True

        record_with_request_id = cast(RequestIDLogRecord, record)
        assert record_with_request_id.request_id == "test-request-id"
    finally:
        request_id_var.reset(token)


def test_request_id_filter_defaults_to_a_placeholder_outside_a_request() -> None:
    record = _make_record()
    assert RequestIDFilter().filter(record) is True

    record_with_request_id = cast(RequestIDLogRecord, record)
    assert record_with_request_id.request_id == "-"


def test_json_formatter_produces_valid_json_with_expected_fields() -> None:
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
    )

    record = _make_record()
    record.msg = "hello, json"
    record.request_id = "abc-123"

    parsed = json.loads(formatter.format(record))

    assert parsed["message"] == "hello, json"
    assert parsed["request_id"] == "abc-123"
    assert parsed["levelname"] == "INFO"
