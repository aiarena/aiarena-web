"""Local development helpers."""

import click

from deploy import docker
from deploy.utils import timing


@click.group()
def dev():
    """Local development commands."""


@dev.command("manage-py", help="Run a Django management command in the dev container")
@click.argument("command", type=str, default="--help")
def manage_py(command):
    docker.cli(f"exec -i aiarena_dev bash -c 'cd /code/ && python manage.py {command}'")


@dev.command("build-image", help="Build dev image")
@timing
def build_image():
    tag = {"latest"}
    docker.build_image("env", tag)
    docker.build_image("dev", tag)
