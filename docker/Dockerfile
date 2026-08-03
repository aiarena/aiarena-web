# Single multi-stage build for all three images. Build a specific one with
# `--target env|dev|cloud`.
#
# These used to be three separate Dockerfiles, with dev/cloud doing
# `FROM aiarena/env` and relying on the local Docker daemon's image store to
# supply that base. That only works with the legacy builder: buildx runs the
# build in an isolated BuildKit container, which has no access to the daemon's
# images and so tries to resolve `aiarena/env` from Docker Hub. Expressing the
# relationship as stages keeps it inside a single build, where BuildKit resolves
# it directly from source.

# ==============================================================================
# Env - base image with system deps, prod python deps, and the code
# ==============================================================================
FROM python:3.12.7-slim-bullseye AS env

ENV UV_PROJECT_ENVIRONMENT=/usr/local

RUN apt update && apt install -y \
        build-essential \
        lsb-release \
        make \
        gcc \
        wget \
        curl \
        gnupg2 \
        git

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# PostgreSQL
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt update && apt install -y postgresql-client-15

# Sentry CLI
RUN curl -sL https://sentry.io/get-cli/ | bash

# Only install deps
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN uv sync --locked --no-dev

# As a last step, actually copy all the code
COPY . /app

ENV PYTHONDONTWRITEBYTECODE=1


# ==============================================================================
# Dev - env plus the dev dependency group
# ==============================================================================
FROM env AS dev

ENV DJANGO_ENVIRONMENT=DEVELOPMENT

RUN uv sync --locked --dev


# ==============================================================================
# Cloud - production image with collected static files
# ==============================================================================
FROM env AS cloud

ENV DJANGO_ENVIRONMENT=PRODUCTION
ARG SECRET_KEY

COPY . /app/

RUN python /app/manage.py collectstatic --noinput --clear

VOLUME /app
