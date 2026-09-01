from typing import cast

from rest_framework.generics import RetrieveUpdateAPIView

from .models import User
from .serializers import UserSerializer


class MeView(RetrieveUpdateAPIView):  # type: ignore[type-arg]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return cast(User, self.request.user)
