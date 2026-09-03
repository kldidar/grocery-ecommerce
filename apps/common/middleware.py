import logging
import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.common.logging import request_id_var

logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        started_at = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - started_at) * 1000, 2)
        logger.info(
            "%s %s %s",
            request.method,
            request.path,
            response.status_code,
            extra={"status_code": response.status_code, "duration_ms": duration_ms},
        )
        return response
