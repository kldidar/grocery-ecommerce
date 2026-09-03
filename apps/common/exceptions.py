import logging
from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.logging import request_id_var

logger = logging.getLogger(__name__)

_STATUS_CODE_LABELS: dict[int, str] = {
    400: "validation_error",
    401: "not_authenticated",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    415: "unsupported_media_type",
    429: "throttled",
}


def _error_code_for(exc: Exception, status_code: int) -> str:

    if status_code in _STATUS_CODE_LABELS:
        return _STATUS_CODE_LABELS[status_code]
    return getattr(exc, "default_code", "error")


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:

    response = drf_exception_handler(exc, context)

    if response is None:
        request_id = request_id_var.get()
        logger.exception("Unhandled exception (request_id=%s)", request_id)
        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                    "details": {"request_id": request_id},
                }
            },
            status=500,
        )

    if isinstance(response.data, dict) and "detail" in response.data:
        message = str(response.data["detail"])
        details = None
    else:
        message = "Validation failed."
        details = response.data

    response.data = {
        "error": {
            "code": _error_code_for(exc, response.status_code),
            "message": message,
            "details": details,
        }
    }
    return response
