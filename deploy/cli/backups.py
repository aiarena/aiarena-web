"""Production DB backup and restore."""

from datetime import UTC, datetime
from pathlib import Path

import click

from deploy import aws
from deploy.session import get_boto3_session
from deploy.settings import (
    DB_NAME,
    PRODUCTION_DB_ROOT_USER,
    PROJECT_PATH,
)
from deploy.stack_outputs import fetch_stack_outputs
from deploy.utils import echo, run, timing


def _confirm_restore(filename):
    confirm = input(  # nosec
        f"Your local DB will be overwritten from {filename}\nContinue (y/N)? ",
    )
    if confirm.lower() == "y":
        return True
    echo("Backup restore cancelled, exiting")
    return False


@click.group()
def backups():
    """Production DB backup operations."""


@backups.command(help="Make a production DB backup and upload it to S3")
@timing
def create():
    now = datetime.now(UTC).replace(microsecond=0)
    filename = "{}_{}.dump".format(
        DB_NAME,
        now.isoformat("_").replace(":", "-"),
    )
    backup_file = f"/tmp/{filename}"  # nosec
    stack_outputs = fetch_stack_outputs()
    password = aws.get_secrets()["POSTGRES_ROOT_PASSWORD"]
    host = stack_outputs.main_db_endpoint
    bucket = stack_outputs.backups_bucket
    pg_dump_cmd = f"PGPASSWORD={password} pg_dump -U {PRODUCTION_DB_ROOT_USER} -h {host} {DB_NAME} -Fc -f {backup_file}"
    s3_mv_cmd = f"aws s3 mv {backup_file} s3://{bucket}/"

    echo("Spinning up a temporary task for the backup...")
    cluster_id, task_id, container_name = aws.create_one_off_task(
        stack_outputs=stack_outputs,
        custom_command=["bash", "-c", f"{pg_dump_cmd} && {s3_mv_cmd}"],
        cpu="256",
        memory="1024",
    )

    echo(f"Waiting for backup task {task_id} to finish...")
    aws.wait_for_task_status(cluster_id, task_id, "STOPPED")
    exit_code = aws.get_task_exit_code(cluster_id, task_id, container_name)

    echo(f"Logs for task {task_id}:")
    aws.print_task_logs(cluster_id, task_id, container_name)

    if exit_code != 0:
        raise RuntimeError(f"Backup task failed with exit code {exit_code}")


@backups.command(help="Restore a DB backup locally")
@click.argument("filename", default="")
@click.option("--host", default="localhost")
@click.option("--port", default="8832")
@click.option("--user", default="aiarena")
@click.option("--password", default="aiarena")
@click.option("--s3", "s3", flag_value="s3", default=None)
@click.option("--quiet", "quiet", flag_value="quiet", default=None)
@timing
def restore(
    filename,
    s3,
    quiet,
    host,
    port,
    user,
    password,
):
    """
    For this command to work, you need to have Postgres running,
    and the credentials specified in the DATABASES setting must
    be correct for a user with admin privileges (i.e. create/drop DBs).

    The default credentials / host / port match the local dev docker-compose.
    """

    if s3:
        stack_outputs = fetch_stack_outputs()
        bucket = stack_outputs.backups_bucket
        s3_client = get_boto3_session().client("s3")
        response = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=1000)
        backups_listing = response.get("Contents", [])
        filenames = sorted(obj["Key"] for obj in backups_listing)
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
        s3_client.download_file(Bucket=bucket, Key=filename, Filename=str(local_file))
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

    echo("Dropping and re-creating the DB...")
    run(
        [
            "dropdb",
            "--if-exists",
            f"--username={user}",
            f"--host={host}",
            f"--port={port}",
            f"{DB_NAME}",
        ],
        env={"PGPASSWORD": password},
    )
    run(
        [
            "createdb",
            f"--username={user}",
            f"--host={host}",
            f"--port={port}",
            f"{DB_NAME}",
        ],
        env={"PGPASSWORD": password},
    )

    echo("Restoring DB backup...")
    run(
        [
            "pg_restore",
            "--no-acl",
            f"--username={user}",
            f"--host={host}",
            f"--port={port}",
            f"--dbname={DB_NAME}",
            f"./backup/{filename}",
        ],
        env={"PGPASSWORD": password},
    )

    echo("Done.")
