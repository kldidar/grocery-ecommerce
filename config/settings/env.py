from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    """Strongly typed representation of the project's environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Django
    django_secret_key: str = Field(min_length=32)
    django_debug: bool = False

    # PostgreSQL
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/1"

    # Email
    default_from_email: str = "noreply@example.com"

    email_host: str = ""
    email_port: int = 587
    email_host_user: str = ""
    email_host_password: str | None = None
    email_use_tls: bool = True
    email_use_ssl: bool = False

    # Minio
    minio_root_user: str
    minio_root_password: str
    minio_bucket_name: str = "media"
    minio_endpoint_url: str = "http://minio:9000"

    cors_allowed_origins: str = ""

    # Security hardening
    allowed_hosts: str = "localhost,127.0.0.1"
    csrf_trusted_origins: str = ""
    jwt_signing_key: str | None = None


env = EnvSettings()  # type: ignore[call-arg]
