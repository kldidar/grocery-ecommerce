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
