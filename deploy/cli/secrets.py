"""AWS Secrets Manager CLI."""

import json
import sys

import click

from deploy import aws
from deploy.utils import echo


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


@secrets.command(help="Securely store key-value pair in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
@click.argument("value")
def set(key, value, secret_id):
    aws.store_secret(key, value, secret_id)


@secrets.command("set-from-file", help="Securely store value from file in AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
@click.argument("filename")
def set_from_file(key, filename, secret_id):
    with open(filename) as source:
        value = source.read()
    aws.store_secret(key, value, secret_id)


@secrets.command(help="Remove a secret from AWS Secrets Manager")
@click.option("--secret-id", default="production-env")
@click.argument("key")
def delete(key, secret_id):
    aws.remove_secret(key, secret_id)
