# Grocery E-Commerce Backend

Production-ready backend for a grocery e-commerce platform, built with
Django and Django REST Framework.

## Status

🚧 Early development. Core infrastructure is in place: containerized
environment, typed configuration, code-quality gates, CI, and a REST API
scaffold with OpenAPI documentation. Business domains (catalog, cart,
orders, payments, notifications) and the two AI modules (visual search,
ingredient scanner) are not implemented yet.

## Tech stack

| Layer | Choice |
|---|---|
| Language / runtime | Python 3.12 |
| Framework | Django 6.1, Django REST Framework 3.17 |
| Database | PostgreSQL 18 (pgvector planned, for the AI modules) |
| Cache / broker | Redis 8 |
| API docs | OpenAPI 3 via drf-spectacular (Swagger UI, ReDoc) |
| Dependency management | [uv](https://docs.astral.sh/uv/) |
| Containerization | Docker, Docker Compose |
| Code quality | Ruff (lint + format), mypy (strict), Bandit |
| Testing | pytest, pytest-django, coverage |
| CI | GitHub Actions |

Planned, not yet integrated: Celery, MinIO, django-unfold, JWT authentication.

## Project structure

```text
apps/            Business applications: users, catalog, cart, orders,
                  payments, notifications, ai, common. Each owns its
                  models, views, and tests (apps/<name>/tests/).
config/          Django project package: settings (config/settings/),
                  root URL configuration.
docs/            Project documentation.
docker/          Docker-related support files.
scripts/         Operational scripts (e.g. scripts/test.sh).
tests/           Cross-application integration tests.
```

`apps/common` holds abstractions shared across applications — see
`apps/common/models.py` for the base model mixins.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) — dependency and environment management
- Docker and Docker Compose (for local services)

## Getting started

```bash
cp .env.example .env   # fill in real values
docker compose up --build
docker compose exec web uv run python manage.py migrate
```

The application is available at http://localhost:8000/.

## API documentation

With the stack running:

- Swagger UI — http://localhost:8000/api/docs/
- ReDoc — http://localhost:8000/api/redoc/
- Raw OpenAPI schema — http://localhost:8000/api/schema/
- Health check — http://localhost:8000/api/v1/health/

All versioned business endpoints live under `/api/v1/`.

## Testing

```bash
docker compose up -d   # PostgreSQL and Redis must be running
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
```

## Architecture decisions

Significant, non-obvious technical decisions are recorded as they are
made in [`DECISIONS.md`](DECISIONS.md).
