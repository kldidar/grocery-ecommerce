import pytest
from django.conf import LazySettings


@pytest.fixture(autouse=True)
def _celery_eager(settings: LazySettings) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
