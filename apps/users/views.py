from typing import cast

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .models import User
from .serializers import RegisterSerializer, UserSerializer
from .services import send_verification_email
from .tokens import email_verification_token


@extend_schema_view(
    get=extend_schema(
        tags=["Users"],
        summary="Get my profile",
        description="Retrieve the currently authenticated user's own profile.",
    ),
    patch=extend_schema(
        tags=["Users"],
        summary="Update my profile",
        description=(
            "Partially update the currently authenticated user's own "
            "profile. email is read-only — see UserSerializer."
        ),
    ),
)
class MeView(RetrieveUpdateAPIView):  # type: ignore[type-arg]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return cast(User, self.request.user)


@extend_schema(
    tags=["Authentication"],
    summary="Obtain a JWT token pair",
    description=(
        "Exchange an email and password for an access and a refresh "
        "token. Limited to 5 requests/minute regardless of the general "
        "anonymous rate limit."
    ),
)
class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


@extend_schema(
    tags=["Authentication"],
    summary="Refresh an access token",
    description=(
        "Exchange a valid, non-blacklisted refresh token for a new access token."
    ),
)
class DocumentedTokenRefreshView(TokenRefreshView):
    """TokenRefreshView, documented — no behavioural change."""


@extend_schema(
    tags=["Authentication"],
    summary="Verify a token",
    description=(
        "Check whether a given token is still valid, without returning a new one."
    ),
)
class DocumentedTokenVerifyView(TokenVerifyView):
    """TokenVerifyView, documented — no behavioural change."""


@extend_schema(tags=["Authentication"], summary="Register")
class RegisterView(CreateAPIView[User]):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "registration"

    def perform_create(self, serializer: BaseSerializer[User]) -> None:
        user = cast(User, serializer.save())
        send_verification_email(user, self.request)


class VerifyEmailSerializer(serializers.Serializer[dict[str, object]]):
    uid = serializers.CharField()
    token = serializers.CharField()

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
            raise serializers.ValidationError("Invalid verification link.") from exc

        if not email_verification_token.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired verification link.")

        attrs["user"] = user
        return attrs


@extend_schema(
    tags=["Authentication"],
    summary="Verify email",
)
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return Response({"status": "verified"})


@extend_schema(
    tags=["Authentication"],
    summary="Resend verification email",
)
class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)

        if user.is_verified:
            return Response(
                {"detail": "Already verified."},
                status=400,
            )

        send_verification_email(user, request)

        return Response({"status": "sent"})
