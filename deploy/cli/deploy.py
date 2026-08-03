"""Production deploy commands."""

import click
from ecs_deployer_boto3 import ApplicationUpdater, DeploymentMonitor

from deploy import aws, docker
from deploy.build_commands import (
    build_frontend,
    build_graphql_schema,
    deploy_environment,
)
from deploy.services.config import get_services
from deploy.session import get_boto3_session
from deploy.settings import (
    PRODUCTION_DB_ROOT_USER,
    PROJECT_NAME,
)
from deploy.stack_outputs import fetch_stack_outputs
from deploy.utils import echo, timing


@click.group()
def deploy():
    """Production deployment commands."""


def cloud_tag(build_number: str) -> str:
    return f"cloud-{build_number}-{docker.ARCH_AMD64}"


@deploy.command("prepare-images", help="Prepare and push production images to ECR")
@timing
def prepare_images():
    stack_outputs = fetch_stack_outputs()
    environment, build_number = deploy_environment(stack_outputs)
    echo(f"Build number: {build_number}")

    # dev is consumed locally (it runs graphql_schema below), so it's --load'ed
    # into the local daemon rather than pushed. No need to build env first: it's
    # a stage of the same Dockerfile, so this build produces it along the way.
    docker.build_image("dev", arch=docker.ARCH_AMD64)
    build_graphql_schema(environment, img="dev")
    build_frontend()

    aws.build_and_push_image(
        "cloud",
        cloud_tag(build_number),
        arch=docker.ARCH_AMD64,
        build_args={"SECRET_KEY": "temporary-secret-key"},  # Does not stay in the image, just for build
    )

    docker.remove_unused_local_images()


@deploy.command("migrate-and-update", help="Run migrations, then update services on ECS")
@timing
def migrate_and_update():
    stack_outputs = fetch_stack_outputs()
    environment, build_number = deploy_environment(stack_outputs)
    services = get_services(stack_outputs)

    # Reconstruct the URI that prepare-images pushed, via the same tag +
    # image_uri helpers, so the manifest references exactly what was built.
    aws.push_manifest("cloud", "latest", [aws.image_uri("cloud", cloud_tag(build_number))])

    # Migrate the production DB as a one-off ECS task inside the VPC, rather
    # than pulling the image onto the CI runner and connecting to RDS from
    # there. We piggyback on a celery service's task definition: single
    # container, same app image, and its security group already reaches RDS.
    # It references cloud:latest — the tag just repointed by push_manifest
    # above — so the migration runs the NEW code while the live services still
    # run the old one (zero-downtime ordering: migrate first, then update).
    migration_base = next(s for s in services if s.name == f"{PROJECT_NAME}-celeryWorker-Default")

    # Run migrations as the root db user, to prevent long-running migrations
    # from being killed by Slow Query Killer (tm), which kills queries only for
    # the regular user.
    aws.run_ecs_task_and_wait(
        stack_outputs=stack_outputs,
        task_definition_id=migration_base.task_definition.family,
        container_name=migration_base.task_definition.containers[0].name,
        command=["python", "-B", "/app/manage.py", "migrate", "-v", "0", "--noinput"],
        description="Migrating production DB",
        environment_override={
            "POSTGRES_USER": PRODUCTION_DB_ROOT_USER,
            "POSTGRES_PASSWORD": environment["POSTGRES_ROOT_PASSWORD"],
        },
    )

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
