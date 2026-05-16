"""Production DB backup and restore."""

from datetime import UTC, datetime
from pathlib import Path

import click
import questionary

from deploy import aws
from deploy.session import get_boto3_session
from deploy.settings import (
    DB_NAME,
    PRODUCTION_DB_ROOT_USER,
    PROJECT_PATH,
)
from deploy.stack_outputs import fetch_stack_outputs
from deploy.utils import echo, run, timing


LOCAL_BACKUP_DIR = PROJECT_PATH / "backup"


def _confirm_restore(filename):
    confirm = input(  # nosec
        f"Your local DB will be overwritten from {filename}\nContinue (y/N)? ",
    )
    if confirm.lower() == "y":
        return True
    echo("Backup restore cancelled, exiting")
    return False


def _format_size(size_bytes: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _format_age(dt: datetime) -> str:
    seconds = int((datetime.now(UTC) - dt).total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours ago"
    days = hours // 24
    return f"{days} days ago"


def _list_s3_backups() -> list[tuple[str, int, datetime]]:
    """List S3 backups, newest first. Returns (filename, size, modified)."""
    stack_outputs = fetch_stack_outputs()
    bucket = stack_outputs.backups_bucket
    s3 = get_boto3_session().client("s3")
    contents = s3.list_objects_v2(Bucket=bucket, MaxKeys=1000).get("Contents", [])
    return sorted(
        [(obj["Key"], obj["Size"], obj["LastModified"]) for obj in contents],
        key=lambda x: x[0],
        reverse=True,
    )


def _list_local_backups() -> list[tuple[str, int, datetime]]:
    """List local backups, newest first. Returns (filename, size, modified)."""
    if not LOCAL_BACKUP_DIR.exists():
        return []
    result = []
    for f in LOCAL_BACKUP_DIR.iterdir():
        if not f.is_file():
            continue
        stat = f.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
        result.append((f.name, stat.st_size, mtime))
    return sorted(result, key=lambda x: x[2], reverse=True)


def _select_s3_backup() -> str | None:
    """Interactively pick an S3 backup and download it locally. Returns filename."""
    backups_list = _list_s3_backups()
    if not backups_list:
        echo("The backups S3 bucket is empty")
        return None

    choices = [
        questionary.Choice(
            title=f"{filename}  ({_format_size(size)}, {_format_age(modified)})",
            value=filename,
        )
        for filename, size, modified in backups_list
    ]
    filename = questionary.select(
        "Select backup (type to filter):",
        choices=choices,
    ).unsafe_ask()

    stack_outputs = fetch_stack_outputs()
    local_file = LOCAL_BACKUP_DIR / filename
    echo(f"Downloading: S3 -> ./backup/{filename}")
    s3 = get_boto3_session().client("s3")
    s3.download_file(stack_outputs.backups_bucket, filename, str(local_file))
    return filename


def _select_local_backup() -> str | None:
    """Interactively pick a local backup. Returns filename."""
    local_list = _list_local_backups()
    if not local_list:
        echo("./backup directory is empty")
        return None

    choices = [
        questionary.Choice(
            title=f"{filename}  ({_format_size(size)}, {_format_age(modified)})",
            value=filename,
        )
        for filename, size, modified in local_list
    ]
    return questionary.select(
        "Select backup (type to filter):",
        choices=choices,
    ).unsafe_ask()


@click.group()
def backups():
    """Production DB backup operations."""


@backups.command("create-production", help="Make a production DB backup and upload it to S3")
@timing
def create_production():
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


@backups.command("create-local", help="Dump local DB to ./backup/")
@click.option("--host", default="localhost")
@click.option("--port", default="8832")
@click.option("--user", default="aiarena")
@click.option("--password", default="aiarena")
@timing
def create_local(host, port, user, password):
    now = datetime.now(UTC).replace(microsecond=0)
    filename = "{}_local_{}.dump".format(
        DB_NAME,
        now.isoformat("_").replace(":", "-"),
    )
    LOCAL_BACKUP_DIR.mkdir(exist_ok=True)
    out_path = LOCAL_BACKUP_DIR / filename

    echo(f"Dumping local DB to ./backup/{filename}...")
    run(
        [
            "pg_dump",
            f"--username={user}",
            f"--host={host}",
            f"--port={port}",
            "-Fc",
            "-f",
            str(out_path),
            DB_NAME,
        ],
        env={"PGPASSWORD": password},
    )
    echo("Done.")


@backups.command("list-production", help="List backups in S3")
def list_production():
    backups_list = _list_s3_backups()
    if not backups_list:
        echo("The backups S3 bucket is empty")
        return
    for filename, size, modified in backups_list:
        echo(f"{filename}  ({_format_size(size)}, {_format_age(modified)})")


@backups.command("list-local", help="List backups in ./backup/")
def list_local():
    local_list = _list_local_backups()
    if not local_list:
        echo("./backup directory is empty")
        return
    for filename, size, modified in local_list:
        echo(f"{filename}  ({_format_size(size)}, {_format_age(modified)})")


@backups.command("restore-local", help="Restore a DB backup locally")
@click.argument("filename", default="")
@click.option("--host", default="localhost")
@click.option("--port", default="8832")
@click.option("--user", default="aiarena")
@click.option("--password", default="aiarena")
@click.option("--s3", "s3", flag_value="s3", default=None)
@click.option("--quiet", "quiet", flag_value="quiet", default=None)
@timing
def restore_local(
    filename,
    s3,
    quiet,
    host,
    port,
    user,
    password,
):
    """Restore a backup into the local DB.

    Postgres must be running locally and the credentials must be for a user
    with admin privileges (create/drop DBs). Defaults match docker-compose.

    With no filename and no --s3, an interactive picker prompts for source
    and file. Pass --s3 (uses latest) or a filename for non-interactive use.
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
        local_file = LOCAL_BACKUP_DIR / filename
        echo(f"Downloading: S3 -> ./backup/{filename}")
        s3_client.download_file(Bucket=bucket, Key=filename, Filename=str(local_file))
    elif filename:
        # Allow providing absolute and relative path, not just filename,
        # this enables using terminal completion to choose the backup file
        options = [
            LOCAL_BACKUP_DIR / filename,
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
        if not quiet and not _confirm_restore(f"./backup/{filename}"):
            return
    else:
        source = questionary.select(
            "Restore from:",
            choices=[
                questionary.Choice("S3 bucket (production backups)", value="s3"),
                questionary.Choice("Local ./backup directory", value="local"),
            ],
        ).unsafe_ask()
        if source == "s3":
            filename = _select_s3_backup()
        else:
            filename = _select_local_backup()
        if not filename:
            return
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
