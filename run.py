#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
import questionary
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
    SERVICES,
)
from deploy.utils import echo, env_as_cli_args, run, timing


@click.group()
def cli():
    pass


@cli.command(help="Get value(s) stored in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key", default="")
def get_secret(secret_id, key):
    secrets_dict = aws.get_secrets(secret_id)
    if key:
        if key not in secrets_dict:
            echo(f"Secret not found in Secrets Manager: {key}")
            sys.exit(1)
        click.echo(secrets_dict[key])
        return
    click.echo(json.dumps(secrets_dict, indent=2, sort_keys=True))


@cli.command(help="Remove a secret from AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
def remove_secret(key, secret_id):
    aws.remove_secret(key, secret_id)


@cli.command(help="Securely store key-value pair in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
@click.argument("value")
def store_secret(key, value, secret_id):
    aws.store_secret(key, value, secret_id)


@cli.command(help="Securely store value from file in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
@click.argument("filename")
def store_secret_file(key, filename, secret_id):
    with open(filename) as source:
        value = source.read()
    aws.store_secret(key, value, secret_id)


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
    try:
        REDIS_CACHE_DB = int(os.environ.get("BUILD_NUMBER", "")) % 5 + 5
    except ValueError:
        REDIS_CACHE_DB = 5

    build_number = os.environ.get("BUILD_NUMBER", "")
    media_bucket = aws.physical_name(PROJECT_NAME, "mediaProductionBucket")
    media_domain = aws.s3_domain(media_bucket)
    environment = {
        "AWS_REGION": AWS_REGION,
        "BUILD_NUMBER": build_number,
        "POSTGRES_HOST": aws.db_endpoint(PROJECT_NAME, "MainDB"),
        "POSTGRES_DATABASE": DB_NAME,
        "POSTGRES_USER": PRODUCTION_DB_USER,
        "REDIS_HOST": aws.cache_cluster_nodes(PROJECT_NAME)[0],
        "REDIS_CACHE_DB": "%s" % REDIS_CACHE_DB,
        "C_FORCE_ROOT": "1",  # force Celery to run as root
        "MAINTENANCE_MODE": str(MAINTENANCE_MODE),
        "DJANGO_ALLOW_ASYNC_UNSAFE": "1",
        "MEDIA_URL": f"https://{media_domain}/",
        "MEDIA_BUCKET": media_bucket,
    }
    environment.update(aws.get_secrets())
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
    application_updater = aws.ApplicationUpdater()
    application_updater.update_application(environment)


@cli.command(help="Deploy dry run")
@timing
def deploy_dry_run():
    environment, build_number = deploy_environment()
    updater = aws.ApplicationUpdater(dry_run=True)
    updater.update_application(environment)


@cli.command(help="Monitor ECS deployment")
@timing
def monitor_ecs():
    aws.monitor_ecs_cluster(
        stack_name=PROJECT_NAME,
        services=SERVICES,
        limit_minutes=7,
    )


@cli.command(help="Spin up a new ECS task, and connect to it")
@click.option("--lifetime-hours", default=24)
@click.option("--dont-kill-on-disconnect", is_flag=True)
@click.option("--cpu")
@click.option("--memory")
def production_one_off_task(lifetime_hours, dont_kill_on_disconnect, cpu, memory):
    task_definitions = aws.task_definitions()
    task_definition_id = questionary.select("Select the base task definition & revision", task_definitions).unsafe_ask()

    container_names = aws.task_definition_container_names(task_definition_id)
    if len(container_names) > 1:
        container_name = questionary.select(
            "This task definition has multiple containers, pick the one to connect to",
            container_names,
        ).ask()
    else:
        container_name = container_names[0]

    clusters = aws.all_clusters()
    cluster_id = questionary.select("Choose the ECS cluster", clusters).unsafe_ask()

    cpu = aws.clean_fargate_cpu(cpu)
    memory = aws.clean_fargate_memory(cpu, memory)

    echo("Running ECS task...")
    result = aws.cli(
        "ecs run-task",
        {
            "cluster": cluster_id,
            "capacity-provider-strategy": [
                {"capacityProvider": "FARGATE_SPOT", "weight": 1},
            ],
            "enable-execute-command": "",
            "task-definition": task_definition_id,
            "overrides": {
                "containerOverrides": [
                    {
                        "name": container_name,
                        "command": ["sleep", str(lifetime_hours * 60 * 60)],
                    },
                ],
                "cpu": cpu,
                "memory": memory,
            },
            "network-configuration": aws.get_network_configuration(),
        },
    )
    task_id = result["tasks"][0]["taskArn"].split("/")[-1]

    aws.connect_to_ecs_task(cluster_id, task_id)

    if not dont_kill_on_disconnect:
        aws.cli(
            "ecs stop-task",
            {"cluster": cluster_id, "task": task_id},
            parse_output=True,
        )
        echo(f"Task {task_id} stopped")


@cli.command(help="Get a secure connection to a running ECS task")
@click.option("--task-id")
def production_attach_to_task(task_id):
    clusters = aws.all_clusters()
    cluster_id = questionary.select("First, choose an ECS cluster", clusters).unsafe_ask()
    if not task_id:
        services = aws.cluster_services(cluster_id)
        service_id = questionary.select("Then, pick the service", services).unsafe_ask()
        tasks = aws.service_tasks(cluster_id, service_id)
        task_id = questionary.select("Finally, select the task ID", tasks).unsafe_ask()

    aws.connect_to_ecs_task(cluster_id, task_id)


def backup_cmd(**kwargs):
    command = "PGPASSWORD={password} pg_dump -U {user} -h {host} {db} -Fc -f {filename}".format(**kwargs)
    return f"bash -c '{command}'"


def _find_first_task_id():
    clusters = aws.all_clusters()
    cluster_id = clusters[0]
    services = aws.cluster_services(cluster_id)
    service_id = [service for service in services if "webService" in service][0]
    tasks = aws.service_tasks(cluster_id, service_id)
    task_id = tasks[0]
    return cluster_id, task_id


@cli.command(help="Make a production DB backup and upload it to S3")
@timing
def production_backup():
    # Pick one of production servers
    cluster_id, task_id = _find_first_task_id()

    # Make a DB backup on that server
    now = datetime.now(timezone.utc).replace(microsecond=0)
    filename = "{}_{}.dump".format(
        DB_NAME,
        now.isoformat("_").replace(":", "-"),
    )
    backup_file = f"/tmp/{filename}"  # nosec
    backup_command = backup_cmd(
        user=PRODUCTION_DB_ROOT_USER,
        password=aws.get_secrets()["POSTGRES_ROOT_PASSWORD"],
        host=aws.db_endpoint(PROJECT_NAME, "MainDB"),
        db=DB_NAME,
        filename=backup_file,
    )

    echo(f"Making backup on task_id == {task_id}...")
    aws.execute_command(cluster_id, task_id, backup_command, interactive=True)

    # Move the backup to S3
    bucket = aws.physical_name(PROJECT_NAME, "backupsBucket")

    echo("Uploading to S3...")
    aws.execute_command(cluster_id, task_id, f"aws s3 mv {backup_file} s3://{bucket}/", interactive=True)


def _confirm_restore(filename):
    confirm = input(  # nosec
        f"Your local DB will be overwritten from {filename}\n" f"Continue (y/N)? ",
    )
    if confirm.lower() == "y":
        return True
    echo("Backup restore cancelled, exiting")
    return False


@cli.command(help="Restore DB backup locally")
@click.argument("filename", default="")
@click.option("--s3", "s3", flag_value="s3", default=None)
@click.option("--quiet", "quiet", flag_value="quiet", default=None)
@timing
def restore_backup(filename, s3, quiet):
    if s3:
        bucket = aws.physical_name(PROJECT_NAME, "backupsBucket")
        backups = aws.cli(
            "s3api list-objects-v2",
            {
                "bucket": bucket,
                "max-items": 1000,
            },
        )["Contents"]
        filenames = sorted(obj["Key"] for obj in backups)
        if not filenames:
            echo("The backups S3 bucket is empty")
            return
        filename = filename or filenames[-1]
        s3_filenames = [fn for fn in filenames if filename in fn]
        if not s3_filenames:
            echo(f"File not found: s3://{bucket}/{filename}*")
            return
        elif len(s3_filenames) > 1:
            echo(f"More than one file found: {s3_filenames[:5]}")
            return
        filename = s3_filenames[0]
        if not quiet and not _confirm_restore(f"s3://{bucket}/{filename}"):
            return
        local_file = PROJECT_PATH / "backup" / filename
        echo(f"Downloading: S3 -> ./backup/{filename}")
        aws.cli(f"s3 cp s3://{bucket}/{filename} {local_file}")
    else:
        if filename:
            # Allow providing absolute and relative path, not just filename,
            # this enables using terminal completion to choose the backup file
            options = [
                PROJECT_PATH / "backup" / filename,
                PROJECT_PATH / filename,
                Path(filename),
            ]
            for option in options:
                if option.exists():
                    filename = option.name
                    break
            else:
                echo(f"File not found: ./backup/{filename}")
                return
        else:
            filenames = sorted((PROJECT_PATH / "backup").iterdir())
            if not filenames:
                echo("./backup directory is empty")
                return
            filename = filenames[-1].name
        if not quiet and not _confirm_restore(f"./backup/{filename}"):
            return

    DB_USER = "aiarena"
    DB_PASSWORD = "aiarena"

    echo("Dropping and re-creating the DB...")
    run(f"dropdb -U {DB_USER} {DB_NAME}", env={"PGPASSWORD": DB_PASSWORD})
    run(f"createdb -U {DB_USER} {DB_NAME}", env={"PGPASSWORD": DB_PASSWORD})

    echo("Restoring DB backup...")
    run(f"pg_restore -U {DB_USER} -d {DB_NAME} ./backup/{filename}", env={"PGPASSWORD": DB_PASSWORD})

    echo("Done.")


@cli.command(help="Build dev image")
@timing
def build_dev_image():
    tag = {"latest"}
    docker.build_image("env", tag)
    docker.build_image("dev", tag)


if __name__ == "__main__":
    cli()
