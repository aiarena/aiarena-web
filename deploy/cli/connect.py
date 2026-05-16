"""Connect to running production ECS tasks."""

import click
import questionary

from deploy import aws
from deploy.session import get_boto3_session
from deploy.stack_outputs import fetch_stack_outputs
from deploy.utils import echo


def _pick_cluster():
    clusters = aws.all_clusters()
    if not clusters:
        raise RuntimeError("No ECS clusters found")
    if len(clusters) == 1:
        return clusters[0]
    return questionary.select("Choose an ECS cluster", clusters).unsafe_ask()


@click.group()
def connect():
    """Open interactive sessions on production tasks."""


@connect.command("one-off-task", help="Spin up a new ECS task and connect to it")
@click.option("--lifetime-hours", default=24)
@click.option("--dont-kill-on-disconnect", is_flag=True)
@click.option("--cpu")
@click.option("--memory")
def one_off_task(lifetime_hours, dont_kill_on_disconnect, cpu, memory):
    stack_outputs = fetch_stack_outputs()

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

    cluster_id = _pick_cluster()

    cluster_id, task_id, container_name = aws.create_one_off_task(
        stack_outputs=stack_outputs,
        cluster_id=cluster_id,
        task_definition_id=task_definition_id,
        container_name=container_name,
        lifetime_hours=lifetime_hours,
        cpu=cpu,
        memory=memory,
    )

    aws.connect_to_ecs_task(cluster_id, task_id, container_name)

    if not dont_kill_on_disconnect:
        get_boto3_session().client("ecs").stop_task(cluster=cluster_id, task=task_id)
        echo(f"Task {task_id} stopped")


@connect.command(help="Attach to a running ECS task")
@click.option("--task-id")
@click.option("--container-name")
def attach(task_id, container_name):
    cluster_id = _pick_cluster()

    if task_id:
        task = aws.describe_tasks(cluster_id, [task_id])[task_id]
    else:
        services = aws.cluster_services(cluster_id)
        service_id = questionary.select("Pick the service", services).unsafe_ask()
        tasks = aws.service_tasks(cluster_id, service_id)
        task = questionary.select(
            "Select the task ID",
            [
                questionary.Choice(
                    title=task_id,
                    value=task,
                )
                for task_id, task in tasks.items()
            ],
        ).unsafe_ask()
        task_id = task["id"]

    if len(task["containers"]) > 1 and not container_name:
        container_name = questionary.select(
            "Task has multiple containers, select the container to connect to",
            [container["name"] for container in task["containers"]],
        ).unsafe_ask()

    aws.connect_to_ecs_task(cluster_id, task_id, container_name)
