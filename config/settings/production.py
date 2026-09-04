from copy import deepcopy

from .base import *  # noqa: F401, F403
from .base import LOGGING as BASE_LOGGING
from .base import MAILERS as BASE_MAILERS
from .env import env

DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in env.allowed_hosts.split(",") if host.strip()]

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in env.csrf_trusted_origins.split(",") if origin.strip()
]

MAILERS = deepcopy(BASE_MAILERS)
MAILERS["default"] = {
    "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "OPTIONS": {
        "host": env.email_host,
        "port": env.email_port,
        "username": env.email_host_user,
        "password": env.email_host_password,
        "use_tls": env.email_use_tls,
        "use_ssl": env.email_use_ssl,
    },
}

LOGGING = deepcopy(BASE_LOGGING)
LOGGING["handlers"]["console"]["formatter"] = "json"

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
