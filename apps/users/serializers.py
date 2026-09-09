from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import LoginEvent, User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "avatar", "created_at"]
        read_only_fields = ["id", "email", "created_at"]


class RegisterSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict[str, object]) -> User:
        return User.objects.create_user(**validated_data)  # type: ignore[arg-type]


class LoginEventSerializer(serializers.ModelSerializer[LoginEvent]):
    class Meta:
        model = LoginEvent
        fields = ["id", "ip_address", "user_agent", "created_at"]
        read_only_fields = ["id", "ip_address", "user_agent", "created_at"]
