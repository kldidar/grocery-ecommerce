# Groery E-Commerce Backend

Production-ready backend for a grocery e-commerce platform, built with
Django and Django REST Framework.

## Status

🚧 Early development. Core infrastructure is complete: containerized
environment, typed configuration, authentication, background task
processing, object storage, structured logging, and security hardening.
Business domains (catalog, cart, orders, payments) and the two AI modules
(visual search, ingredient scanner) are not implemented yet.

## Features implemented so far

- Custom, email-based user model with JWT authentication (rotation +
  blacklisting) and a dedicated, strict rate limit on login attempts
- User profile with avatar upload, validated by content (not just
  extension) before being stored
- Asynchronous email delivery via Celery, with a dedicated service layer
- S3-compatible object storage (MinIO), interchangeable with Amazon S3
  without business-logic changes
- Structured (JSON in production) logging with per-request correlation
  IDs
- A single, consistent error response shape across the entire API
- CORS, security headers, and Django's own deployment security checklist
  enforced in CI

## Tech stack

| Layer | Choice |
|---|---|
| Language / runtime | Python 3.12 |
| Framework | Django 6.1, Django REST Framework 3.17 |
| Database | PostgreSQL 18 (pgvector planned, for the AI modules) |
| Cache / broker | Redis 8 |
| Background tasks | Celery |
| Object storage | MinIO (S3-compatible) |
| API docs | OpenAPI 3 via drf-spectacular (Swagger UI, ReDoc) |
| Dependency management | [uv](https://docs.astral.sh/uv/) |
| Containerization | Docker, Docker Compose |
| Code quality | Ruff (lint + format), mypy (strict), Bandit |
| Testing | pytest, pytest-django, coverage |
| CI | GitHub Actions |

Planned, not yet integrated: django-unfold (admin panel), pgvector + CLIP
(AI visual search), OCR (ingredient scanner).

## Project structure

```text
apps/            Business applications: users, catalog, cart, orders,
                  payments, notifications, ai, common. Each owns its
                  models, views, and tests (apps/<name>/tests/).
config/          Django project package: settings (config/settings/),
                  root and versioned URL configuration, Celery app.
docs/            Project documentation (see docs/ARCHITECTURE.md).
docker/          Docker-related support files.
scripts/         Operational scripts (e.g. scripts/test.sh).
tests/           Cross-application integration tests.
```

`apps/common` holds abstractions shared across applications: base model
mixins, structured-logging support, the global exception handler, and
custom middleware.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) — dependency and environment management
- Docker and Docker Compose (for local services)

## Getting started

```bash
cp .env.example .env   # fill in real values — see "Environment variables" below
docker compose up --build
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py createsuperuser
```

The application is available at http://localhost:8000/.

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Cryptographic signing key (min. 32 characters) | — *(required)* |
| `DJANGO_DEBUG` | Enable debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames (production) | `localhost,127.0.0.1` |
| `POSTGRES_DB` / `_USER` / `_PASSWORD` / `_HOST` / `_PORT` | PostgreSQL connection | — |
| `REDIS_URL` | Redis — cache and rate limiting (logical DB 0) | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Celery (logical DB 1) | `redis://redis:6379/1` |
| `DEFAULT_FROM_EMAIL` | Sender address for outgoing email | `noreply@example.com` |
| `MINIO_ROOT_USER` / `_PASSWORD` / `_BUCKET_NAME` / `_ENDPOINT_URL` | Object storage | — |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed cross-origin hosts | *(empty — closed)* |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins (production) | *(empty)* |
| `JWT_SIGNING_KEY` | Optional, separate JWT signing key | falls back to `DJANGO_SECRET_KEY` |

## API documentation

With the stack running:

- Swagger UI — http://localhost:8000/api/docs/
- ReDoc — http://localhost:8000/api/redoc/
- Raw OpenAPI schema — http://localhost:8000/api/schema/
- Health check — http://localhost:8000/api/v1/health/

All versioned business endpoints live under `/api/v1/`. Errors follow a
single shape across the entire API:

```json
{"error": {"code": "not_authenticated", "message": "...", "details": null}}
```

Every response carries an `X-Request-ID` header, useful for correlating
a specific request with its log entries.

## Authentication

JWT (access + refresh tokens):

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -d "email=you@example.com&password=yourpassword"

curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <access token>"

curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -d "refresh=<refresh token>"
```

Access tokens last 15 minutes, refresh tokens 7 days, with rotation and
blacklisting enabled. The token-obtain endpoint has its own, much
stricter rate limit (5/minute) separate from the general API limits
(100/hour anonymous, 1000/hour authenticated).

## Background tasks

Celery, with Redis as broker and result backend:

```bash
docker compose up -d          # includes a dedicated `worker` service
docker compose logs worker    # observe task execution
```

Currently implemented: asynchronous email delivery
(`apps.notifications.services.NotificationService`).

## Testing

```bash
docker compose up -d   # PostgreSQL, Redis, and MinIO must be running
./scripts/test.sh
```

Runs the suite via pytest with coverage measured through `coverage`
(configuration in `pyproject.toml`). Target: 90% by project completion —
see `DECISIONS.md`, ADR-001.

## Code quality

Enforced locally (pre-commit) and in CI (GitHub Actions):

```bash
uv run ruff check .                    # lint
uv run ruff format --check .           # formatting
uv run mypy .                          # static typing
uv run bandit -c pyproject.toml -r .   # security
uv run python manage.py check --deploy --settings=config.settings.production
```

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the system
architecture and current entity-relationship diagram.

## Architecture decisions

Significant, non-obvious technical decisions are recorded as they are
made in [`DECISIONS.md`](DECISIONS.md).
