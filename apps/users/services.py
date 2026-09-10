from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.request import Request

from apps.notifications.services import NotificationService
from apps.users.models import User

from .tokens import email_verification_token


def _send_token_email(
    user: User,
    request: Request,
    token_generator: object,
    url_path: str,
    subject: str,
    action_description: str,
) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)  # type: ignore[attr-defined]
    url = request.build_absolute_uri(f"{url_path}?uid={uid}&token={token}")

    NotificationService.send_email(
        subject=subject,
        message=f"{action_description}: {url}",
        recipient_list=[user.email],
    )


def send_verification_email(user: User, request: Request) -> None:
    _send_token_email(
        user,
        request,
        email_verification_token,
        "/api/v1/auth/verify-email/",
        "Confirm your email",
        "Confirm your email by submitting a POST to",
    )


def send_password_reset_email(user: User, request: Request) -> None:
    _send_token_email(
        user,
        request,
        default_token_generator,
        "/api/v1/auth/password-reset/confirm/",
        "Reset your password",
        "Reset your password by submitting a POST to",
    )
