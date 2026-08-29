# syntax=docker/dockerfile:1

# Slim, Debian-based Python 3.12 runtime image.
FROM python:3.12-slim

# Copy the pinned `uv` binary from Astral's distroless image. Pinning an
# explicit version (rather than `:latest`) keeps builds reproducible.
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /uvx /bin/

# uv-related environment configuration:
# - UV_PROJECT_ENVIRONMENT: place the virtual environment at /venv, outside
#   of /app. In development, /app is bind-mounted from the host for hot
#   reload; keeping the environment outside that path prevents the mounted
#   host directory from hiding or overwriting the environment built here.
# - UV_LINK_MODE=copy: copy packages into the environment instead of
#   hard-linking them, required when the cache and the environment can
#   reside on different filesystems (relevant with mounted volumes).
# - UV_COMPILE_BYTECODE=1: pre-compile .pyc files during `uv sync` so the
#   application starts faster, instead of compiling on first import.
# - UV_PYTHON_DOWNLOADS=never: the base image already provides Python 3.12;
#   uv must not attempt to download its own managed interpreter.
ENV UV_PROJECT_ENVIRONMENT=/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/venv/bin:$PATH"

WORKDIR /app

# Install dependencies in their own layer, before the application source
# code is copied in. pyproject.toml and uv.lock change far less often than
# the source tree, so this layer is reused by Docker's cache on most
# rebuilds. `--no-install-project` installs only third-party dependencies,
# since the project itself has not been copied in yet.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the rest of the application source code.
COPY . .

# Re-sync now that the full project is present. Dependencies were already
# installed in the previous layer, so this step is fast.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]