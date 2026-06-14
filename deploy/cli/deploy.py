"""Production deploy commands."""

import json
import os

import click
from ecs_deployer_boto3 import ApplicationUpdater, DeploymentMonitor

from deploy import aws, docker
from deploy.build_commands import (
    build_frontend,
    build_graphql_schema,
    deploy_environment,
    set_github_actions_output,
)
from deploy.services.config import get_services
from deploy.session import get_boto3_session
from deploy.settings import (
    PRODUCTION_DB_ROOT_USER,
    PROJECT_NAME,
)
from deploy.stack_outputs import fetch_stack_outputs
from deploy.utils import echo, env_as_cli_args, timing


@click.group()
def deploy():
    """Production deployment commands."""


@deploy.command("prepare-images", help="Prepare and push production images to ECR")
@timing
def prepare_images():
    stack_outputs = fetch_stack_outputs()
    environment, build_number = deploy_environment(stack_outputs)
    echo(f"Build number: {build_number}")

    docker.build_image("env", arch=docker.ARCH_AMD64)
    docker.build_image("dev", arch=docker.ARCH_AMD64)
    build_graphql_schema(environment, img="dev")
    build_frontend()

    cloud_tag = f"cloud-{build_number}-{docker.ARCH_AMD64}"
    docker.build_image(
        "cloud",
        tag=cloud_tag,
        arch=docker.ARCH_AMD64,
        build_args={"SECRET_KEY": "temporary-secret-key"},  # Does not stay in the image, just for build
    )

    cloud_images = aws.push_images("cloud", [cloud_tag])
    echo(f"Saving images to github output: {json.dumps({'cloud_images': cloud_images})}")
    set_github_actions_output("images", json.dumps({"cloud_images": cloud_images}))

    docker.remove_unused_local_images()


@deploy.command("migrate-and-update", help="Run migrations, then update services on ECS")
@timing
def migrate_and_update():
    stack_outputs = fetch_stack_outputs()
    environment, build_number = deploy_environment(stack_outputs)
    images = json.loads(os.environ.get("PREPARED_IMAGES"))

    aws.push_manifest("cloud", "latest", images["cloud_images"])

    # Prepare different environment with root db user for migrations. This is
    # required in order to prevent long-running migrations from being killed by
    # Slow Query Killer (tm) which kills queries only for regular user
    root_environment = environment.copy()
    root_environment["POSTGRES_USER"] = PRODUCTION_DB_ROOT_USER
    root_environment["POSTGRES_PASSWORD"] = root_environment["POSTGRES_ROOT_PASSWORD"]

    aws.pull_image("cloud:latest")

    # Migrate production DB and load initial data
    manage_py_cmd = "python -B /app/manage.py"
    docker.cli(
        f"run --rm {env_as_cli_args(root_environment)} "
        f"{PROJECT_NAME}/cloud "
        f'bash -c "{manage_py_cmd} migrate -v 0 --noinput"',
    )
    services = get_services(stack_outputs)
    application_updater = ApplicationUpdater(services, get_boto3_session())
    application_updater.update_application(environment)


@deploy.command("dry-run", help="Show what a deploy would do without applying it")
@timing
def dry_run():
    stack_outputs = fetch_stack_outputs()
    environment, _ = deploy_environment(stack_outputs)
    services = get_services(stack_outputs)
    updater = ApplicationUpdater(services, get_boto3_session(), dry_run=True)
    updater.update_application(environment)


@deploy.command(help="Monitor ECS deployment until it stabilizes")
@timing
def monitor():
    services = get_services(fetch_stack_outputs())
    monitor = DeploymentMonitor(services, get_boto3_session())
    monitor.monitor(limit_minutes=10)
