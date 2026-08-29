# Food E-Commerce Backend

Production-ready backend for a food e-commerce platform, built with Django.

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