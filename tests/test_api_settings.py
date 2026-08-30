from django.conf import settings


def test_default_permission_is_authenticated() -> None:

    assert settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] == [
        "rest_framework.permissions.IsAuthenticated"
    ]


def test_pagination_is_configured() -> None:

    assert settings.REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] == (
        "rest_framework.pagination.PageNumberPagination"
    )
