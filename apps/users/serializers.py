from typing import cast

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.users.models import LoginEvent, User
from apps.users.services import blacklist_all_tokens_for


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


class PasswordResetRequestSerializer(serializers.Serializer[dict[str, object]]):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer[User]):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        uid = cast(str, attrs["uid"])
        token = cast(str, attrs["token"])

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (
            User.DoesNotExist,
            ValueError,
            TypeError,
            OverflowError,
        ) as exc:
            raise serializers.ValidationError("Invalid reset link.") from exc

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired reset link.")

        new_password = cast(str, attrs["new_password"])
        validate_password(new_password, user=user)

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict[str, object]) -> User:
        user = cast(User, validated_data["user"])
        new_password = cast(str, validated_data["new_password"])

        user.set_password(new_password)
        user.save(update_fields=["password"])

        blacklist_all_tokens_for(user)

        return user
