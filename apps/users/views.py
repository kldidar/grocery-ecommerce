from typing import cast

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .models import User
from .serializers import UserSerializer


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
    description="Exchange a valid, non-blacklisted refresh token for a new access token.",
)
class DocumentedTokenRefreshView(TokenRefreshView):
    """TokenRefreshView, documented — no behavioural change."""


@extend_schema(
    tags=["Authentication"],
    summary="Verify a token",
    description="Check whether a given token is still valid, without returning a new one.",
)
class DocumentedTokenVerifyView(TokenVerifyView):
    """TokenVerifyView, documented — no behavioural change."""
