from typing import cast

from django.db.models import QuerySet
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
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

from apps.users.models import LoginEvent, User
from apps.users.serializers import (
    LoginEventSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)
from apps.users.services import send_password_reset_email, send_verification_email
from apps.users.tokens import email_verification_token


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

    def post(self, request: Request, *args: object, **kwargs: object) -> Response:
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            data = cast(dict[str, object], request.data)
            email = str(data.get("email", ""))

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
            else:
                LoginEvent.objects.create(
                    user=user,
                    ip_address=request.META.get("REMOTE_ADDR") or "127.0.0.1",
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
                )

        return response


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
        user = serializer.save()
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


@extend_schema(tags=["Users"], summary="My login history")
class LoginHistoryView(ListAPIView[LoginEvent]):
    serializer_class = LoginEventSerializer

    def get_queryset(self) -> QuerySet[LoginEvent]:
        user = cast(User, self.request.user)
        return user.login_events.all()


@extend_schema(tags=["Authentication"], summary="Request a password reset")
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "reset"

    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email__iexact=serializer.validated_data["email"])
        except User.DoesNotExist:
            pass
        else:
            send_password_reset_email(user, request)
        return Response(
            {
                "detail": "If an account with that email exists, a reset link has been sent."
            }
        )


@extend_schema(tags=["Authentication"], summary="Confirm a password reset")
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "reset_confirm"

    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "password_reset_complete"})
