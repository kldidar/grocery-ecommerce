# Grocery E-Commerce Backend

Production-ready backend for a grocery e-commerce platform, built with Django.

## Status
🚧 Under active development. Stage 0 — environment setup.

## Tech stack
Django · DRF · PostgreSQL (+pgvector) · Redis · Celery · MinIO · django-unfold

## Requirements
- Python 3.12
- [uv](https://docs.astral.sh/uv/) — dependency and environment management
- Docker and Docker Compose (for local services)

## Getting started

1. Copy `.env.example` to `.env` and fill in real values.
2. `docker compose up --build`
3. The application is available at http://localhost:8000/

## Code quality

This project enforces style, typing, and security checks locally (via
pre-commit) and in CI (via GitHub Actions):

```bash
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy .                # static typing
uv run bandit -c pyproject.toml -r .  # security
```
