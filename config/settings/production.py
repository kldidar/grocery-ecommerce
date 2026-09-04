from copy import deepcopy

from .base import *  # noqa: F401, F403
from .base import LOGGING as BASE_LOGGING

DEBUG = False

ALLOWED_HOSTS.clear()  # noqa: F405

LOGGING = deepcopy(BASE_LOGGING)
LOGGING["handlers"]["console"]["formatter"] = "json"


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
