import logging

from django.http import HttpRequest, JsonResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView

from apps.common.logging import request_id_var
from apps.common.serializers import HealthCheckSerializer


@extend_schema(
    responses=HealthCheckSerializer,
    tags=["Infrastructure"],
    summary="Health check",
    description=(
        "Unauthenticated, unthrottled liveness probe for load balancers "
        "and uptime monitors."
    ),
)
class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    throttle_classes: list[type[BaseThrottle]] = []

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})


@extend_schema(exclude=True)
class PublicSpectacularAPIView(SpectacularAPIView):
    permission_classes = [AllowAny]


class PublicSpectacularSwaggerView(SpectacularSwaggerView):
    permission_classes = [AllowAny]


class PublicSpectacularRedocView(SpectacularRedocView):
    permission_classes = [AllowAny]


def handler404(request: HttpRequest, exception: Exception) -> JsonResponse:

    return JsonResponse(
        {"error": {"code": "not_found", "message": "Not found.", "details": None}},
        status=404,
    )


def handler500(request: HttpRequest) -> JsonResponse:

    request_id = request_id_var.get()
    logging.getLogger(__name__).exception(
        "Unhandled exception outside DRF dispatch (request_id=%s)", request_id
    )
    return JsonResponse(
        {
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred.",
                "details": {"request_id": request_id},
            }
        },
        status=500,
    )
