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
# Base - the runtime OS layer, shared by the builder and the final images
# ==============================================================================
FROM python:3.12.7-slim-bullseye AS base

ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Runtime-only system deps. The compilers needed to BUILD python packages are
# deliberately not here — they live in the deps stage below, so ~340MB of
# toolchain never reaches the shipped image. curl/gnupg2/lsb-release/wget are
# needed by the psql + sentry-cli installs that follow.
RUN apt update && apt install -y \
        lsb-release \
        wget \
        curl \
        gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# PostgreSQL client (psql, for ./manage.py dbshell & making backups)
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt update && apt install -y postgresql-client-15 \
    && rm -rf /var/lib/apt/lists/*

# Sentry CLI
RUN curl -sL https://sentry.io/get-cli/ | bash


# ==============================================================================
# Deps - compiles and installs the python dependencies. Nothing from this stage
# ships except the resulting /usr/local, so the toolchain and uv's download
# cache stay out of the runtime image.
# ==============================================================================
FROM base AS deps

RUN apt update && apt install -y \
        build-essential \
        make \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock /app/
# --no-cache: uv's download cache is ~400MB and is useless at runtime. Without
# it the cache lands in /usr/local's layer and gets copied into the image.
RUN uv sync --locked --no-cache --no-dev


# ==============================================================================
# Code - just the application source, as a stage so env and dev share one
# definition of what "the code" is instead of two copies that can drift.
#
# This is a WHITELIST, not `COPY . /app` plus a .dockerignore blacklist: the
# blacklist had silently gone stale (it ignored `frontend/node_modules` long
# after the SPA moved, and never covered .venv), so ~930MB of host virtualenv
# and node_modules was shipping in the image and being pulled on every cold ECS
# task start. With a whitelist, forgetting an entry breaks the container loudly
# instead of quietly inflating the image.
#
# nginx/ is needed at runtime: aiarena/nginx.sh copies /app/nginx/* into
# /etc/nginx/. The .dockerignore still applies on top of these, to keep
# node_modules and caches out of the directories copied here.
# ==============================================================================
FROM base AS code

COPY manage.py /app/
COPY nginx /app/nginx
COPY aiarena /app/aiarena

# frontend-spa is a frontend BUILD tree (node config, src/, public/, and the
# built assets). At runtime Django needs only the vite manifest out of it, and
# nginx serves the assets from /app/static — so it is dropped here and the
# manifest is copied back in the cloud stage. Keeping it cost ~79MB, most of it
# a second copy of what collectstatic already produced.
#
# Removed in the same layer that added it: deleting it in a later layer would
# leave the bytes in this one. Copying aiarena/ wholesale and then pruning
# beats listing its siblings individually, which would silently fail to ship a
# newly added Django app.
RUN rm -rf /app/aiarena/frontend-spa


# ==============================================================================
# Env - runtime base: the OS layer plus the installed deps and the code
# ==============================================================================
FROM base AS env

# UV_PROJECT_ENVIRONMENT is /usr/local, so the installed deps (and the compiled
# uwsgi binary) come across in one copy, without the compilers that built them.
COPY --from=deps /usr/local /usr/local
COPY --from=code /app /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1


# ==============================================================================
# Dev - the dev dependency group on top of the build toolchain.
#
# Built FROM deps, not env: installing the dev group needs uv and the compilers,
# which env deliberately doesn't have. Dev images are only ever run locally and
# in CI, never pulled by Fargate, so their size doesn't matter.
# ==============================================================================
FROM deps AS dev

ENV DJANGO_ENVIRONMENT=DEVELOPMENT
ENV PYTHONDONTWRITEBYTECODE=1

RUN uv sync --locked --dev

# Same code as the runtime image (so without frontend-spa). That's fine: the
# dev image is always run with the repo bind-mounted over /app, which shadows
# whatever is baked in here.
COPY --from=code /app /app


# ==============================================================================
# Static - runs collectstatic. A throwaway stage: only /app/static is copied
# out of it, so the frontend-spa SOURCE assets that collectstatic reads never
# reach the runtime image.
#
# Deleting them in a later layer would not help — the bytes would still sit in
# the layer that added them — so the read has to happen in a stage that is
# itself discarded.
# ==============================================================================
FROM env AS static

# The frontend build output, consumed by collectstatic via STATICFILES_DIRS.
COPY aiarena/frontend-spa/static /app/aiarena/frontend-spa/static

ARG SECRET_KEY
RUN DJANGO_ENVIRONMENT=PRODUCTION python /app/manage.py collectstatic --noinput --clear


# ==============================================================================
# Cloud - production image with collected static files
# ==============================================================================
FROM env AS cloud

ENV DJANGO_ENVIRONMENT=PRODUCTION

COPY --from=static /app/static /app/static

# django-vite reads this manifest on every render to resolve asset URLs, from
# the SOURCE path (STATICFILES_DIRS), not from the collected copy — and
# collectstatic skips it anyway, since it ignores dot-prefixed directories. So
# it is the one part of frontend-spa/ the runtime genuinely needs; the rest of
# the assets are served from /app/static.
COPY --from=static /app/aiarena/frontend-spa/static/dist/.vite/manifest.json \
     /app/aiarena/frontend-spa/static/dist/.vite/manifest.json

VOLUME /app
