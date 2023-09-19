#!/usr/bin/env python3
import json
import os
import sys

import click
import yaml

from deploy import aws, docker
from deploy.settings import (
    AWS_REGION,
    DB_NAME,
    MAINTENANCE_MODE,
    PRODUCTION_DB_ROOT_USER,
    PRODUCTION_DB_USER,
    PROJECT_NAME,
    PROJECT_PATH,
    SECRETS_FOLDER,
    SERVICES,
)
from deploy.utils import echo, env_as_cli_args, timing


@click.group()
def cli():
    pass


@cli.command(help=f'Get value(s) stored in "{SECRETS_FOLDER}"')
@click.argument("key", default="")
def get_secret(key):
    if key:
        key_path = PROJECT_PATH / SECRETS_FOLDER / key
        if not key_path.is_file():
            echo(f"File not found: {key_path}")
            sys.exit(1)
        click.echo(aws.decrypt_secret(key))
        return
    click.echo(json.dumps(aws.decrypt_secrets(), indent=2, sort_keys=True))


def _store_secret(key, value):
    outfile = f"{SECRETS_FOLDER}/{key}"
    with (PROJECT_PATH / outfile).open("wb") as f:
        f.write(aws.encrypt_secret(value))
    echo(f"Saved to {outfile}")


@cli.command(help=f'Securely store key-value pair in "{SECRETS_FOLDER}"')
@click.argument("key")
@click.argument("value")
def store_secret(key, value):
    _store_secret(key, value)


@cli.command(help=f'Securely store value from file in "{SECRETS_FOLDER}"')
@click.argument("key")
@click.argument("filename")
def store_secret_file(key, filename):
    with open(filename) as source:
        value = source.read()
    _store_secret(key, value)


@cli.command(help="Management command")
@click.argument("command", type=str, default="--help")
def manage_py(command):
    _manage_py("aiarena_dev", "", command)


def _manage_py(env_container, comment, args):
    echo(comment)
    docker.cli(f"exec -i {env_container} bash -c 'cd /code/ && python manage.py {args}'")


@cli.command(help="Generate cloudformation template")
def cloudformation():
    region = "default"
    source = f"index-{region}.yaml"
    target = f"cloudformation-{region}.yaml"
    file_path = PROJECT_PATH / target
    with file_path.open("w") as f:
        f.write(yaml.dump(aws.cloudformation_load(source), sort_keys=False))
    echo(f"Saved to {target}")
    echo("OK")


def deploy_environment():
    build_number = os.environ.get("BUILD_NUMBER", "")
    media_bucket = aws.physical_name(PROJECT_NAME, "mediaTestBucket")
    media_domain = aws.s3_domain(PROJECT_NAME, "mediaTestBucket")
    environment = {
        "AWS_REGION": AWS_REGION,
        "BUILD_NUMBER": build_number,
        "POSTGRES_HOST": aws.db_endpoint(PROJECT_NAME, "MainDB"),
        "POSTGRES_DATABASE": DB_NAME,
        "POSTGRES_USER": PRODUCTION_DB_USER,
        "MAINTENANCE_MODE": str(MAINTENANCE_MODE),
        "DJANGO_ALLOW_ASYNC_UNSAFE": "1",
        "MEDIA_URL": f"https://{media_domain}/",
        "MEDIA_BUCKET": media_bucket,
    }
    environment.update(aws.decrypt_secrets())
    return environment, build_number


def set_github_actions_output(key, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    with open(output_file, "a") as f:
        f.write(f"{key}={value}\n")


@cli.command(help="Prepare and push production images to ECR")
@timing
def prepare_images():
    environment, build_number = deploy_environment()
    echo(f"Build number: {build_number}")

    docker.build_image("env", arch=docker.ARCH_AMD64)

    base_tag = f"build-{build_number}"

    tag_amd64 = f"{base_tag}-{docker.ARCH_AMD64}"
    docker.build_image(
        "cloud",
        tag=tag_amd64,
        arch=docker.ARCH_AMD64,
        build_args={"SECRET_KEY": "temporary-secret-key"},  # Does not stay in the image, just for build
    )

    cloud_images = aws.push_images("cloud", [tag_amd64])
    set_github_actions_output(
        "images",
        json.dumps({"cloud_images": cloud_images}),
    )

    docker.remove_unused_local_images()


@cli.command(help="Deploy to Amazon ECS")
@timing
def ecs():
    environment, build_number = deploy_environment()
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
    aws.update_all_services(environment)


@cli.command(help="Monitor ECS deployment")
@timing
def monitor_ecs():
    aws.monitor_ecs_cluster(
        stack_name=PROJECT_NAME,
        services=SERVICES,
        limit_minutes=7,
    )


def _find_instance_id(server_number: int) -> str | None:
    logical_id = "ECSCluster"
    servers = aws.cluster_ec2_instances(PROJECT_NAME, logical_id)
    if server_number < 0 or server_number > len(servers) - 1:
        echo(f"Wrong server number, should be between 0-{len(servers) - 1}")
        return None
    return servers[server_number]["InstanceId"]


@cli.command(help="SSH to production web server")
@click.argument("server-number", type=int, default=-1)
@click.option("--instance-id", default="")
def production_ssh(server_number, instance_id):
    if server_number == -1 and not instance_id:
        click.echo("Please provide either server_number or instance_id")
        return

    instance_id = instance_id or _find_instance_id(server_number)
    if not instance_id:
        return

    echo(f"Connecting to instance_id = {instance_id}")
    aws.cli(
        "ssm start-session"
        f" --target {instance_id}"
        ' --document-name AWS-StartInteractiveCommand --parameters command="bash -l"',
        parse_output=False,
    )


@cli.command(help="Build dev image")
@timing
def build_dev_image():
    tag = {"latest"}
    docker.build_image("env", tag)
    docker.build_image("dev", tag)


if __name__ == "__main__":
    cli()
