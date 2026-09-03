from copy import deepcopy

from .base import *  # noqa: F401, F403
from .base import LOGGING as BASE_LOGGING

DEBUG = False

ALLOWED_HOSTS.clear()  # noqa: F405

LOGGING = deepcopy(BASE_LOGGING)
LOGGING["handlers"]["console"]["formatter"] = "json"
