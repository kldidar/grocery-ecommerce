from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.request import Request

from apps.notifications.services import NotificationService
from apps.users.models import User

from .tokens import email_verification_token


def send_verification_email(user: User, request: Request) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verify_url = request.build_absolute_uri(
        f"/api/v1/auth/verify-email/?uid={uid}&token={token}"
    )

    NotificationService.send_email(
        subject="Confirm your email",
        message=f"Confirm your email by submitting a POST to: {verify_url}",
        recipient_list=[user.email],
    )
