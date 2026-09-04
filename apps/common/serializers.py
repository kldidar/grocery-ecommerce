from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):  # type: ignore[type-arg]
    status = serializers.CharField()
