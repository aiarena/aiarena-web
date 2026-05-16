"""Infrastructure helpers."""

import click
import yaml

from deploy import aws
from deploy.settings import PROJECT_PATH
from deploy.utils import echo


@click.group()
def infra():
    """Infrastructure commands."""


@infra.command(help="Render the CloudFormation template to a flat YAML file")
def cloudformation():
    region = "default"
    source = f"index-{region}.yaml"
    target = f"cloudformation-{region}.yaml"
    file_path = PROJECT_PATH / target
    with file_path.open("w") as f:
        f.write(yaml.dump(aws.cloudformation_load(source), sort_keys=False))
    echo(f"Saved to {target}")
    echo("OK")
