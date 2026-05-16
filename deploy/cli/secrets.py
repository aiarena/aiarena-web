"""AWS Secrets Manager CLI."""

import json
import secrets as stdlib_secrets
import string
import sys

import click
import questionary

from deploy import aws
from deploy.utils import echo


def _generate_password(length: int) -> str:
    """Letters + digits only — avoids shell/quoting issues across services."""
    alphabet = string.ascii_letters + string.digits
    return "".join(stdlib_secrets.choice(alphabet) for _ in range(length))


def _prompt_password_length() -> int:
    return int(
        questionary.text(
            "Password length:",
            default="32",
            validate=lambda x: x.isdigit() and int(x) > 0,
        ).unsafe_ask()
    )


def _parse_dotenv(text: str) -> dict[str, str]:
    """Parse dotenv-style KEY=VALUE lines. Skips blanks and `#` comments."""
    updates = {}
    for line_num, raw_line in enumerate(text.strip().split("\n"), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Line {line_num}: missing '=' separator")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Line {line_num}: empty key")
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        updates[key] = value
    return updates


@click.group()
def secrets():
    """Manage values in AWS Secrets Manager."""


@secrets.command(help="Get value(s) stored in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key", default="")
def get(secret_id, key):
    secrets_dict = aws.get_secrets(secret_id)
    if key:
        if key not in secrets_dict:
            echo(f"Secret not found in Secrets Manager: {key}")
            sys.exit(1)
        click.echo(secrets_dict[key])
        return
    click.echo(json.dumps(secrets_dict, indent=2, sort_keys=True))


@secrets.command(help="Set one or more secrets")
@click.option("--secret-id", default="production-env")
@click.option("--generate", is_flag=True, help="Generate a secure random password")
@click.argument("key", required=False)
@click.argument("value", required=False)
def set(key, value, generate, secret_id):
    """Set secret(s).

    \b
    Single key:
        secrets set KEY VALUE
        secrets set KEY --generate

    Batch (no args): paste dotenv-style KEY=VALUE lines.
    """
    if key is None:
        if generate:
            echo("--generate requires a KEY")
            sys.exit(1)

        echo("Enter KEY=VALUE pairs (one per line, Ctrl+D when done):")
        text = questionary.text("Paste KEY=VALUE pairs:", multiline=True).unsafe_ask()
        if not text:
            echo("No input provided.")
            sys.exit(1)

        try:
            updates = _parse_dotenv(text)
        except ValueError as e:
            echo(f"Error parsing input: {e}")
            sys.exit(1)

        if not updates:
            echo("No valid KEY=VALUE pairs found.")
            sys.exit(1)
    else:
        if generate and value:
            echo("Cannot specify both VALUE and --generate")
            sys.exit(1)
        if not generate and value is None:
            echo("Must provide VALUE or use --generate")
            sys.exit(1)
        if generate:
            length = _prompt_password_length()
            value = _generate_password(length)
            echo(f"Generated password: {value}")
        updates = {key: value}

    current = aws.get_secrets(secret_id)
    overrides = sorted(k for k in updates if k in current)
    if overrides:
        echo("Will overwrite existing key(s):")
        for k in overrides:
            echo(f"  - {k}")
        if not questionary.confirm("Continue?", default=False).unsafe_ask():
            echo("Cancelled.")
            sys.exit(0)

    aws.store_secrets(updates, secret_id)
    echo(f"Updated {len(updates)} key(s):")
    for k in updates:
        echo(f"  - {k}")


@secrets.command("set-from-file", help="Store the contents of a file as a single secret value")
@click.option("--secret-id", default="production-env")
@click.argument("key")
@click.argument("filename")
def set_from_file(key, filename, secret_id):
    with open(filename) as source:
        value = source.read()

    current = aws.get_secrets(secret_id)
    if key in current and not questionary.confirm(f"{key} already in secrets. Overwrite?", default=False).unsafe_ask():
        echo("Cancelled.")
        sys.exit(0)

    aws.store_secrets({key: value}, secret_id)
    echo(f"Updated: {key}")


@secrets.command(help="Remove one or more secrets")
@click.option("--secret-id", default="production-env")
@click.argument("keys", nargs=-1, required=True)
def delete(keys, secret_id):
    echo("Keys to delete:")
    for k in keys:
        echo(f"  - {k}")
    if not questionary.confirm(f"Delete {len(keys)} key(s)?", default=False).unsafe_ask():
        echo("Cancelled.")
        sys.exit(0)

    removed = aws.remove_secrets(keys, secret_id)
    missing = [k for k in keys if k not in removed]
    if removed:
        echo(f"Deleted {len(removed)} key(s):")
        for k in removed:
            echo(f"  - {k}")
    for k in missing:
        echo(f"Not found, skipped: {k}")
