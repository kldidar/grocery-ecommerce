from typing import cast

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer


class MeView(RetrieveUpdateAPIView):  # type: ignore[type-arg]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return cast(User, self.request.user)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
