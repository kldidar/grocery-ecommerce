from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import User


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp: int) -> str:
        return f"{user.pk}{user.is_verified}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
