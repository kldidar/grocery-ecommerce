from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView

from apps.common.serializers import HealthCheckSerializer


@extend_schema(responses=HealthCheckSerializer)
class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    throttle_classes: list[type[BaseThrottle]] = []

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})
