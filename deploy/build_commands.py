"""Build-time helpers shared between deploy commands."""

import os
from pathlib import Path

from . import aws, docker
from .settings import (
    AWS_REGION,
    DB_NAME,
    MAINTENANCE_MODE,
    PRODUCTION_DB_USER,
    PROJECT_NAME,
)
from .stack_outputs import StackOutputs
from .utils import echo, env_as_cli_args, run


def deploy_environment(stack_outputs: StackOutputs):
    try:
        REDIS_CACHE_DB = int(os.environ.get("BUILD_NUMBER", "")) % 5 + 5
    except ValueError:
        REDIS_CACHE_DB = 5

    build_number = os.environ.get("BUILD_NUMBER", "")
    media_bucket = stack_outputs.media_production_bucket
    media_domain = aws.s3_domain(media_bucket)
    environment = {
        "AWS_REGION": AWS_REGION,
        "BUILD_NUMBER": build_number,
        "POSTGRES_HOST": stack_outputs.main_db_endpoint,
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": DB_NAME,
        "POSTGRES_USER": PRODUCTION_DB_USER,
        "REDIS_HOST": stack_outputs.redis_endpoint,
        "REDIS_PORT": "6379",
        "REDIS_CACHE_DB": str(REDIS_CACHE_DB),
        "C_FORCE_ROOT": "1",  # force Celery to run as root
        "MAINTENANCE_MODE": str(MAINTENANCE_MODE),
        "DJANGO_ALLOW_ASYNC_UNSAFE": "1",
        "MEDIA_URL": f"https://{media_domain}/",
        "MEDIA_BUCKET": media_bucket,
    }
    environment.update(aws.get_secrets())
    return environment, build_number


def build_graphql_schema(env: dict | None = None, img: str = "dev") -> None:
    # Run schema generation without build number, since, if it is present,
    # local.py is checked, which we do not have in the env image.
    env_without_build_number = (env or {}).copy()
    env_without_build_number.pop("BUILD_NUMBER", None)
    args = env_as_cli_args(env_without_build_number)
    app_dir = Path.cwd()
    manage_py_cmd = "python -B /app/manage.py"
    docker.cli(
        f'run --rm {args} -v {app_dir}:/app {PROJECT_NAME}/{img} bash -c "{manage_py_cmd} graphql_schema"',
    )


def build_frontend() -> None:
    echo("Build frontend")
    # Regenerate the SPA's URL definitions from urls.py first — like the GraphQL schema
    # it's gitignored and generated, but unlike the schema it's written *into* the Relay
    # `__generated__/` dir, so it must run on the host (not the root build container, which
    # would leave the dir root-owned and break the host-side `npm run relay` that follows).
    run("uv run python manage.py generate_url_definitions")
    run(
        "npm install && npm run relay && npm run build",
        cwd="aiarena/frontend-spa",
    )


def set_github_actions_output(key: str, value: str) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with open(output_file, "a") as f:
        f.write(f"{key}={value}\n")
