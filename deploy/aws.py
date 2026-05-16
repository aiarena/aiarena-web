import base64
import json
import os
import subprocess
import time
from functools import wraps

import questionary

from . import docker
from .session import get_boto3_session
from .settings import (
    AWS_ELB_HEALTH_CHECK_ENDPOINT,
    CONTAINER_INSIGHTS,
    DB_NAME,
    PRIVATE_REGISTRY_URL,
    PRODUCTION_DB_ROOT_USER,
    PROJECT_NAME,
    PROJECT_PATH,
    UWSGI_CONTAINER_NAME,
    WEB_PORT,
)
from .utils import echo
from .yaml_template import load_yaml_template


def get_secrets(secret_id="production-env"):
    client = get_boto3_session().client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_id)
    secrets: dict = json.loads(response["SecretString"])

    # Printing out the special add-mask instruction doesn't show up in
    # GitHub Actions, and instead makes it so that any occurrences of those
    # strings are replaced with asterisks in future output. The idea is that
    # this is the root source of all secret values - they ultimately all come
    # through here, and it's sufficient to just mask them once.
    if os.environ.get("MASK_SECRETS") == "1":
        for secret_value in secrets.values():
            print(f"::add-mask::{secret_value}")

    return secrets


def store_secret(key, value, secret_id="production-env"):
    current_values = get_secrets(secret_id)
    if key in current_values and not questionary.confirm(f"{key} already in secrets. Override?").unsafe_ask():
        raise RuntimeError("Aborting...")

    current_values[key] = value
    client = get_boto3_session().client("secretsmanager")
    client.put_secret_value(SecretId=secret_id, SecretString=json.dumps(current_values))


def remove_secret(key, secret_id="production-env"):
    current_values = get_secrets(secret_id)
    if key not in current_values:
        echo(f"{key} not found in secrets, nothing to do")
        return

    del current_values[key]
    client = get_boto3_session().client("secretsmanager")
    client.put_secret_value(SecretId=secret_id, SecretString=json.dumps(current_values))


def ecr_login():
    """Authenticate the local Docker daemon against ECR."""
    client = get_boto3_session().client("ecr")
    response = client.get_authorization_token()
    auth = response["authorizationData"][0]
    username, password = base64.b64decode(auth["authorizationToken"]).decode().split(":")
    endpoint = auth["proxyEndpoint"]

    subprocess.run(
        ["docker", "login", "--username", username, "--password-stdin", endpoint],
        input=password.encode(),
        check=True,
        capture_output=True,
    )


def ensure_docker_login(func):
    """
    Re-tries the docker operation with login, if needed

    Note: This provides the registry_url argument to the inner function
    """

    @wraps(func)
    def inner(*args, **kwargs):
        kwargs["registry_url"] = PRIVATE_REGISTRY_URL

        try:
            return func(*args, **kwargs)
        except RuntimeError:
            echo("Try adding ECR authorization...")
            ecr_login()
            return func(*args, **kwargs)

    return inner


@ensure_docker_login
def push_image(image, public=False, registry_url=None) -> str:
    echo(f"Pushing image: {image}")
    local_image = f"{PROJECT_NAME}/{image}"
    registry_image = f"{registry_url}/{local_image}"
    docker.cli(f"tag {local_image} {registry_image}")
    docker.cli(f"push {registry_image}", input="\n")
    return registry_image


@ensure_docker_login
def pull_image(image, public=False, registry_url=None):
    echo(f"Pulling image: {image}")
    local_image = f"{PROJECT_NAME}/{image}"
    registry_image = f"{registry_url}/{local_image}"
    docker.cli(f"pull {registry_image}", input="\n")
    docker.cli(f"tag {registry_image} {local_image}")


@ensure_docker_login
def push_images(
    image,
    tags: list[str],
    public=False,
    registry_url=None,
):
    ecr_images: list[str] = []
    for tag in tags:
        ecr_images.append(push_image(f"{image}:{tag}", public=public))
    return ecr_images


@ensure_docker_login
def push_manifest(
    image,
    manifest_tag: str,
    ecr_images: list[str],
    public=False,
    registry_url=None,
):
    echo(f"Creating manifest: {image}:{manifest_tag} from {ecr_images}")
    manifest_name = f"{registry_url}/{PROJECT_NAME}/{image}:{manifest_tag}"
    docker.cli(f"manifest create {manifest_name} {' '.join(ecr_images)}", print_cmd=True)
    docker.cli(f"manifest push --purge {manifest_name}", print_cmd=True)


def task_definitions():
    ecs = get_boto3_session().client("ecs")
    arn_list = ecs.list_task_definitions()["taskDefinitionArns"]
    return [arn.split("/")[-1] for arn in arn_list]


def task_definition_container_names(task_definition):
    ecs = get_boto3_session().client("ecs")
    result = ecs.describe_task_definition(taskDefinition=task_definition)
    return [c["name"] for c in result["taskDefinition"]["containerDefinitions"]]


def all_clusters():
    ecs = get_boto3_session().client("ecs")
    arn_list = ecs.list_clusters()["clusterArns"]
    return [arn.split("/")[-1] for arn in arn_list]


def cluster_services(cluster):
    ecs = get_boto3_session().client("ecs")
    arn_list = ecs.list_services(cluster=cluster)["serviceArns"]
    return [arn.split("/")[-1] for arn in arn_list]


def describe_tasks(cluster, task_list):
    if not task_list:
        return {}
    ecs = get_boto3_session().client("ecs")
    tasks = ecs.describe_tasks(cluster=cluster, tasks=task_list)["tasks"]
    for task in tasks:
        task["id"] = task["taskArn"].split("/")[-1]
    return {task["id"]: task for task in tasks}


def service_tasks(cluster, service):
    ecs = get_boto3_session().client("ecs")
    arn_list = ecs.list_tasks(cluster=cluster, serviceName=service)["taskArns"]
    return describe_tasks(cluster, arn_list)


def execute_command(cluster_id, task_id, command: str, container_name=None):
    """Run an interactive command inside a task via ECS Exec.

    Shells out to the AWS CLI because the underlying SSM session manager plugin
    needs a real TTY — boto3 alone can't drive an interactive session.
    """
    session = get_boto3_session()
    cmd = [
        "aws",
        "ecs",
        "execute-command",
        "--cluster",
        cluster_id,
        "--task",
        task_id,
        "--command",
        command,
        "--interactive",
        "--region",
        session.region_name,
    ]
    # boto3 reports profile_name == "default" when no profile was passed (e.g.
    # under OIDC in CI where credentials come from environment variables). The
    # AWS CLI errors out on `--profile default` when there's no ~/.aws/config,
    # so only forward --profile when we attached a real one in get_boto3_session.
    if session.profile_name and session.profile_name != "default":
        cmd.extend(["--profile", session.profile_name])
    if container_name:
        cmd.extend(["--container", container_name])

    # Retry logic for when execute agent is not ready yet
    max_attempts = 10
    attempts = 0
    while attempts <= max_attempts:
        try:
            subprocess.run(cmd, check=True)
            break
        except subprocess.CalledProcessError as e:
            if attempts == max_attempts:
                raise RuntimeError("Execute agent wasn't available after 10 attempts, giving up :(") from e
            echo("Execute agent not running yet, re-trying in 10s")
            attempts += 1
            time.sleep(10)


def wait_for_task_status(
    cluster_id,
    task_id,
    status,
    check_period_seconds=10,
    give_up_after_seconds=None,
):
    """Wait for an ECS task to reach a status."""
    ecs = get_boto3_session().client("ecs")
    t_start = time.time()

    while True:
        tasks = ecs.describe_tasks(cluster=cluster_id, tasks=[task_id])["tasks"]
        task = tasks[0]
        task_last_status = task["lastStatus"]
        if task_last_status == status:
            break

        # If we're actually waiting for it to stop, we'll break above ^
        if task_last_status == "STOPPED":
            raise RuntimeError(f"Task {task_id} in unexpected STOPPED status")

        if give_up_after_seconds and time.time() > t_start + give_up_after_seconds:
            raise RuntimeError(f"Task {task_id} didn't reach {status} status after {give_up_after_seconds} seconds")

        echo(f"Task {task_id} has status {task_last_status}, waiting {check_period_seconds}s for {status} status ")
        time.sleep(check_period_seconds)


def get_task_exit_code(cluster_id, task_id, container_name):
    ecs = get_boto3_session().client("ecs")
    tasks = ecs.describe_tasks(cluster=cluster_id, tasks=[task_id])["tasks"]
    container = next(c for c in tasks[0]["containers"] if c["name"] == container_name)
    return container.get("exitCode")


def print_task_logs(cluster_id, task_id, container_name):
    """Print CloudWatch logs for an ECS task."""
    session = get_boto3_session()
    ecs = session.client("ecs")
    logs = session.client("logs")

    task = ecs.describe_tasks(cluster=cluster_id, tasks=[task_id])["tasks"][0]
    task_def = ecs.describe_task_definition(taskDefinition=task["taskDefinitionArn"])["taskDefinition"]

    container_def = next(c for c in task_def["containerDefinitions"] if c["name"] == container_name)
    log_config = container_def.get("logConfiguration", {})

    if log_config.get("logDriver") != "awslogs":
        echo("Task is not using CloudWatch logs")
        return

    options = log_config.get("options", {})
    log_group = options.get("awslogs-group")
    log_stream_prefix = options.get("awslogs-stream-prefix", "")

    if not log_group:
        echo("No log group configured for this task")
        return

    if log_stream_prefix:
        log_stream = f"{log_stream_prefix}/{container_name}/{task_id}"
    else:
        log_stream = f"{container_name}/{task_id}"

    try:
        result = logs.filter_log_events(logGroupName=log_group, logStreamNames=[log_stream])
    except logs.exceptions.ResourceNotFoundException:
        echo(f"Log stream not found: {log_stream}")
        return

    events = result.get("events", [])
    if not events:
        echo("No logs found for this task")
        return

    for event in events:
        echo(event["message"], prefix="")


def connect_to_ecs_task(cluster_id, task_id, container_name=None):
    wait_for_task_status(cluster_id, task_id, "RUNNING")

    # Get task details after it's running
    ecs = get_boto3_session().client("ecs")
    task = ecs.describe_tasks(cluster=cluster_id, tasks=[task_id])["tasks"][0]

    if len(task["containers"]) > 1 and not container_name:
        raise ValueError(
            "Cannot connect to task because it has more than one container and container_name wasn't specified",
        )
    elif not container_name:
        container_name = task["containers"][0]["name"]

    echo(f"Connecting to task_id = {task_id}, container = {container_name}")
    execute_command(
        cluster_id,
        task_id,
        "/bin/bash",
        container_name=container_name,
    )


def create_one_off_task(
    stack_outputs,
    cluster_id=None,
    task_definition_id=None,
    container_name=None,
    custom_command: list[str] | None = None,
    lifetime_hours=1,
    *,
    cpu,
    memory,
):
    """Create a new ECS task and wait for it to be ready for commands."""
    if not cluster_id:
        cluster_id = stack_outputs.ecs_cluster

    if not task_definition_id:
        task_definitions_list = task_definitions()
        task_definition_id = task_definitions_list[0]

    if not container_name:
        container_names = task_definition_container_names(task_definition_id)
        container_name = container_names[0]

    cpu = clean_fargate_cpu(cpu)
    memory = clean_fargate_memory(cpu, memory)

    if custom_command:
        command = custom_command
    else:
        command = ["sleep", str(lifetime_hours * 60 * 60)]

    echo(f"Creating ECS task using {task_definition_id}...")
    ecs = get_boto3_session().client("ecs")
    result = ecs.run_task(
        cluster=cluster_id,
        capacityProviderStrategy=[{"capacityProvider": "FARGATE_SPOT", "weight": 1}],
        enableExecuteCommand=True,
        taskDefinition=task_definition_id,
        overrides={
            "containerOverrides": [
                {
                    "name": container_name,
                    "command": command,
                },
            ],
            "cpu": cpu,
            "memory": memory,
        },
        networkConfiguration=get_network_configuration(stack_outputs),
    )
    task_id = result["tasks"][0]["taskArn"].split("/")[-1]

    # Wait for task to be ready
    echo(f"Waiting for task {task_id} to be ready...")
    wait_for_task_status(cluster_id, task_id, "RUNNING")

    return cluster_id, task_id, container_name


def clean_fargate_cpu(value=None):
    valid = [
        "256",
        "512",
        "1024",
        "2048",
        "4096",
        "8192",
        "16384",
    ]
    if value in valid:
        return value
    elif value:
        echo(f"{value} is not a valid CPU value for Fargate")
    return questionary.select("Pick the CPU value", valid).unsafe_ask()


def clean_fargate_memory(cpu_value, value=None):
    # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html
    by_cpu = {
        "256": [0.5, 1, 2],
        "512": list(range(1, 4 + 1)),
        "1024": list(range(2, 8 + 1)),
        "2048": list(range(4, 16 + 1)),
        "4096": list(range(8, 30 + 1)),
        "8192": list(range(16, 60 + 1, 4)),
        "16384": list(range(32, 120 + 1, 8)),
    }
    valid = [str(gib * 1024) for gib in by_cpu[cpu_value]]

    if value in valid:
        return value
    elif value:
        echo(f"{value} is not a valid memory value for a Fargate instance with {cpu_value} CPU")
    return questionary.select("Pick the memory value", valid).unsafe_ask()


def get_network_configuration(stack_outputs):
    return {
        "awsvpcConfiguration": {
            "subnets": [
                stack_outputs.public_subnet_zone_a,
                stack_outputs.public_subnet_zone_b,
            ],
            "securityGroups": [stack_outputs.ecs_task_security_group],
            "assignPublicIp": "ENABLED",
        }
    }


def s3_domain(cf_id) -> str:
    return f"{cf_id}.s3.amazonaws.com"


def cloudformation_load(source="index-default.yaml", skip_secrets=False):
    source_path = PROJECT_PATH / "deploy/cloudformation"

    context = {
        "project_name": PROJECT_NAME,
        "container_insights": "enabled" if CONTAINER_INSIGHTS else "disabled",
        "db_name": DB_NAME,
        "db_master_user": PRODUCTION_DB_ROOT_USER,
        "web_port": WEB_PORT,
        "health_check_path": AWS_ELB_HEALTH_CHECK_ENDPOINT,
        "uwsgi_container_name": UWSGI_CONTAINER_NAME,
    }

    if skip_secrets:
        context["db_master_password"] = ""
    else:
        secrets = get_secrets()
        context["db_master_password"] = secrets["POSTGRES_ROOT_PASSWORD"]

    return load_yaml_template(source_path / source, context=context)
