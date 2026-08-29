from .base import *  # noqa: F401,F403
from .env import env

DEBUG = env.django_debug
ALLOWED_HOSTS = ["*"]