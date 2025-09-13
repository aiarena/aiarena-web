FROM python:3.12.7-slim-bullseye

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
