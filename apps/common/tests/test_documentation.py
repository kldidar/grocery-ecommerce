from rest_framework import status
from rest_framework.test import APIClient


def test_api_docs_are_publicly_accessible() -> None:

    client = APIClient()
    for path in ["/api/schema/", "/api/docs/", "/api/redoc/"]:
        response = client.get(path)
        assert response.status_code == status.HTTP_200_OK, path


def test_openapi_schema_generates_without_errors_and_includes_tags() -> None:

    response = APIClient().get("/api/schema/")
    assert response.status_code == status.HTTP_200_OK
    tag_names = {tag["name"] for tag in response.data["tags"]}
    assert {"Infrastructure", "Authentication", "Users"}.issubset(tag_names)
