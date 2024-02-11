import itertools
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from multiprocessing.pool import ThreadPool
from shlex import quote

import questionary

from . import docker
from .settings import (
    AWS_ELB_HEALTH_CHECK_ENDPOINT,
    AWS_REGION,
    CONTAINER_INSIGHTS,
    DB_NAME,
    PRIVATE_REGISTRY_URL,
    PRODUCTION_DB_ROOT_USER,
    PROJECT_NAME,
    PROJECT_PATH,
    SERVICES,
    UWSGI_CONTAINER_NAME,
    WEB_PORT,
)
from .utils import echo, run
from .yaml_template import load_yaml_template


def cli(
    command: str,
    conf=None,
    region=None,
    parse_output=True,
    capture_stderr=False,
    **kwargs,
):
    def format_value(value):
        if isinstance(value, str):
            return value
        return f"'{json.dumps(value, separators=(',', ':'))}'"

    if conf is None:
        conf = {}
    arguments = " ".join(f"--{k} {format_value(v)}" for k, v in conf.items())
    cmd = f"{command} {arguments}"

    if parse_output:
        kwargs["capture_stdout"] = True
    if capture_stderr:
        kwargs["capture_stderr"] = True

    region = region or AWS_REGION
    if os.environ.get("AWS_ACCESS_KEY_ID"):
        prefix = f"aws --region {region}"
    else:
        profile = os.environ.get("AWS_PROFILE") or PROJECT_NAME
        prefix = f"aws --profile {profile} --region {region}"
    cmd = f"{prefix} {cmd}"

    result = run(cmd, **kwargs)

    if parse_output:
        result = json.loads("".join(result.stdout_lines))

    return result


def get_secrets(secret_id="production-env"):
    secret_string = cli("secretsmanager get-secret-value", {"secret-id": secret_id})["SecretString"]
    return json.loads(secret_string)


def store_secret(key, value, secret_id="production-env"):
    current_values = get_secrets(secret_id)
    if key in current_values and not questionary.confirm(f"{key} already in secrets. Override?").unsafe_ask():
        raise RuntimeError("Aborting...")

    current_values[key] = value
    secret_string = quote(json.dumps(current_values))
    cli("secretsmanager put-secret-value", {"secret-id": secret_id, "secret-string": secret_string})


def remove_secret(key, secret_id="production-env"):
    current_values = get_secrets(secret_id)
    if key not in current_values:
        echo(f"{key} not found in secrets, nothing to do")
        return

    del current_values[key]
    secret_string = quote(json.dumps(current_values))
    cli("secretsmanager put-secret-value", {"secret-id": secret_id, "secret-string": secret_string})


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
            docker_login = cli(
                "ecr get-login",
                {"no-include-email": ""},
                capture_stdout=True,
                parse_output=False,
            ).stdout_lines[0]
            run(docker_login)
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
    docker.cli(f'manifest create {manifest_name} {" ".join(ecr_images)}', print_cmd=True)
    docker.cli(f"manifest push --purge {manifest_name}", print_cmd=True)


def resource_details(stack_name, logical_id):
    return cli(
        "cloudformation describe-stack-resource",
        {"stack-name": stack_name, "logical-resource-id": logical_id},
    )["StackResourceDetail"]


def physical_name(stack_name, logical_id):
    res_id = resource_details(stack_name, logical_id)["PhysicalResourceId"]
    return res_id.split("/")[-1]


def task_definitions():
    arn_list = cli("ecs list-task-definitions")["taskDefinitionArns"]
    return [task_definition_arn.split("/")[-1] for task_definition_arn in arn_list]


def task_definition_container_names(task_definition):
    result = cli(
        "ecs describe-task-definition",
        {"task-definition": task_definition},
    )
    container_definitions = result["taskDefinition"]["containerDefinitions"]
    return [container["name"] for container in container_definitions]


def all_clusters():
    arn_list = cli("ecs list-clusters")["clusterArns"]
    return [cluster_arn.split("/")[-1] for cluster_arn in arn_list]


def cluster_services(cluster):
    arn_list = cli("ecs list-services", {"cluster": cluster})["serviceArns"]
    return [service_arn.split("/")[-1] for service_arn in arn_list]


def service_tasks(cluster, service):
    arn_list = cli("ecs list-tasks", {"cluster": cluster, "service-name": service})["taskArns"]
    return [task_arn.split("/")[-1] for task_arn in arn_list]


def execute_command(cluster_id, task_id, command: str, interactive=True):
    conf = {"cluster": cluster_id, "task": task_id, "command": f'"{command}"'}

    if interactive:
        conf["interactive"] = ""

    cli(
        "ecs execute-command",
        conf,
        parse_output=False,
        capture_stderr=True,
    )


def connect_to_ecs_task(cluster_id, task_id):
    while True:
        tasks = cli(
            "ecs describe-tasks",
            {"cluster": cluster_id, "tasks": task_id},
        )["tasks"]

        task_last_status = tasks[0]["lastStatus"]
        if task_last_status == "RUNNING":
            break

        echo(f"Task {task_id} has status {task_last_status}, waiting 10s for RUNNING status ")
        time.sleep(10)

    echo(f"Connecting to task_id = {task_id}")
    attempts = 10
    while attempts > 0:
        try:
            execute_command(cluster_id, task_id, "/bin/bash", interactive=True)
        except RuntimeError:
            echo("Execute agent not running yet, re-trying in 10s")
            time.sleep(10)
            attempts -= 1
        else:
            break
    else:
        raise RuntimeError("Execute agent wasn't available after 10 attempts, giving up :(")


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


def get_network_configuration():
    return {
        "awsvpcConfiguration": {
            "subnets": [
                physical_name(PROJECT_NAME, "PublicSubnetZoneA"),
                physical_name(PROJECT_NAME, "PublicSubnetZoneB"),
            ],
            "securityGroups": [physical_name(PROJECT_NAME, "ECSTaskSecurityGroup")],
            "assignPublicIp": "ENABLED",
        }
    }


def db_endpoint(stack_name, logical_id):
    db_id = physical_name(stack_name, logical_id)
    db_instance = cli(
        "rds describe-db-instances",
        {"db-instance-identifier": db_id},
    )
    return db_instance["DBInstances"][0]["Endpoint"]["Address"]


def cache_cluster_nodes(logical_id):
    cloudformation = cloudformation_load()
    cl_id = cloudformation["Resources"][logical_id]["Properties"]["ClusterName"]
    result = cli(
        "elasticache describe-cache-clusters",
        {
            "show-cache-node-info": "",
            "cache-cluster-id": cl_id,
        },
    )
    cluster = result["CacheClusters"][0]
    return [n["Endpoint"]["Address"] for n in cluster["CacheNodes"]]


def s3_domain(stack_name: str, logical_id: str) -> str:
    """
    Get S3 bucket domain by stack logical resource ID.
    """
    cf_id = physical_name(stack_name, logical_id)
    return f"{cf_id}.s3.amazonaws.com"


def cloudformation_load(source="index-default.yaml"):
    source_path = PROJECT_PATH / "deploy/cloudformation"
    return load_yaml_template(
        source_path / source,
        context={
            "project_name": PROJECT_NAME,
            "container_insights": "enabled" if CONTAINER_INSIGHTS else "disabled",
            "db_name": DB_NAME,
            "db_master_user": PRODUCTION_DB_ROOT_USER,
            "db_master_password": get_secrets()["POSTGRES_ROOT_PASSWORD"],
            "web_port": WEB_PORT,
            "health_check_path": AWS_ELB_HEALTH_CHECK_ENDPOINT,
            "uwsgi_container_name": UWSGI_CONTAINER_NAME,
        },
    )


def register_task(task_definition):
    echo(f"Registering task definition: {task_definition.get('family', '')}")
    result = cli("ecs register-task-definition", {"cli-input-json": quote(json.dumps(task_definition))})
    revision = int(result["taskDefinition"]["revision"])
    echo(f"Revision registered: {revision}")
    if revision > 1:
        previous = f"{result['taskDefinition']['family']}:{revision - 1}"
        try:
            cli("ecs deregister-task-definition", {"task-definition": previous})
        except RuntimeError as e:
            echo(f"Couldn't de-register previous revision: {e}")
        else:
            echo(f"De-registered previous revision {previous}")
    return result


class ApplicationUpdater:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

        # Find target group ARNs
        self.target_group_arns = {}
        resources = cloudformation_load().get("Resources", {})
        for name, resource in resources.items():
            if resource["Type"] != "AWS::ElasticLoadBalancingV2::TargetGroup":
                continue
            arn = resource_details(PROJECT_NAME, name)["PhysicalResourceId"]
            self.target_group_arns[name] = arn

        # Detect clusters and roles in use (logical -> physical name mapping)
        self.clusters = {}
        self.roles = {}
        for service in SERVICES:
            c = service.cluster_name
            assert c in resources, f"{c} not found in CloudFormation template"
            self.clusters[c] = self.clusters.get(c) or physical_name(PROJECT_NAME, c)

            r = service.role_name
            if not r:
                continue

            aws_roles = {"AWSServiceRoleForECS"}  # They exist by default, not part of our stack
            if r in aws_roles:
                self.roles[r] = r
            else:
                assert r in resources, f"{r} not found in CloudFormation template"
                self.roles[r] = self.roles.get(r) or physical_name(PROJECT_NAME, r)

    @property
    def desired_services(self):
        if len({s.name for s in SERVICES}) != len(SERVICES):
            raise ValueError("Duplicate service name detected")
        return {s.name: s for s in SERVICES if s.count}

    def update_application(self, environment):
        if self.dry_run:
            echo("Running in dry run mode")

        self.update_all_services(environment)
        self.delete_inactive_ecs_task_definitions()

    def update_all_services(self, environment):
        updated = []
        for cluster_name, cluster_id in self.clusters.items():
            existing_services = cli(
                "ecs list-services",
                {"cluster": cluster_id},
            )["serviceArns"]
            for service in existing_services:
                service_name = service.split("/")[-1]
                match = self.match_service_for_update(cluster_name, cluster_id, service_name)
                if match:
                    self.update_service(cluster_id, service_name, match, environment)
                    updated.append(service_name)
                else:
                    self.remove_service(cluster_id, service_name)

        for service_name, match in self.desired_services.items():
            if service_name in updated:
                continue
            self.create_service(service_name, match, environment)

    @staticmethod
    def explain_service_re_create(
        service_name,
        attribute,
        current_value,
        new_value,
    ):
        echo(
            f"{service_name}: {attribute} forces re-creation, "
            f"current value: {current_value}, new value: {new_value}",
        )

    def match_service_for_update(self, cluster_name, cluster_id, service_name):
        match = self.desired_services.get(service_name)

        if not match:
            echo(f"Service {service_name} not found")
            return None

        if match.cluster_name != cluster_name:
            echo(f"Service {service_name} not in cluster {cluster_name}")
            return None

        details = cli(
            "ecs describe-services",
            {
                "service": service_name,
                "cluster": cluster_id,
            },
        )[
            "services"
        ][0]

        task = details["taskDefinition"].split("/")[-1]
        task_family = task.split(":")[0]
        if task_family != match.task.family:
            self.explain_service_re_create(
                service_name,
                "task family",
                task_family,
                match.task.family,
            )
            return None

        role = None
        port = None
        target_group = None
        if details["loadBalancers"]:
            balancer_details = details["loadBalancers"][0]
            port = balancer_details["containerPort"]
            role = details["roleArn"].split("/")[-1]
            target_group = balancer_details.get("targetGroupArn")

        if role != self.roles.get(match.role_name):
            self.explain_service_re_create(
                service_name,
                "role",
                role,
                self.roles.get(match.role_name),
            )
            return None

        if port != match.container_port:
            self.explain_service_re_create(
                service_name,
                "port",
                port,
                match.container_port,
            )
            return None

        if target_group != self.target_group_arns.get(match.target_group):
            self.explain_service_re_create(
                service_name,
                "target group",
                target_group,
                self.target_group_arns.get(match.target_group),
            )
            return None

        return match

    def create_service(self, service_name, match, environment):
        if self.dry_run:
            echo(f"Would have created service {service_name}")
            return

        echo(f"Creating service: {service_name}")
        register_task(match.task.as_dict(environment))

        conf = {
            "service-name": service_name,
            "enable-execute-command": "",
            "capacity-provider-strategy": match.capacity_provider_strategy,
            "cluster": self.clusters[match.cluster_name],
            "task-definition": match.task.family,
            "desired-count": match.count,
            "deployment-configuration": {
                "maximumPercent": match.max_percent,
                "minimumHealthyPercent": match.min_percent,
            },
        }

        if match.container_port is not None:
            target_group = self.target_group_arns[match.target_group]
            conf["load-balancers"] = {
                "targetGroupArn": target_group,
                "containerName": match.container_name,
                "containerPort": match.container_port,
            }
            conf["role"] = self.roles[match.role_name]

        cli("ecs create-service", conf)

        echo(f"Service created: {service_name}")

    def update_service(self, cluster_id, service_name, match, environment):
        if self.dry_run:
            echo(f"Would have updated service {service_name}")
            return

        echo(f"Updating service: {service_name}")
        register_task(match.task.as_dict(environment))
        conf = {
            "service": service_name,
            "cluster": cluster_id,
            "desired-count": match.count,
            "task-definition": match.task.family,
            "enable-execute-command": "",
            "capacity-provider-strategy": match.capacity_provider_strategy,
            "force-new-deployment": "",
            "deployment-configuration": {
                "maximumPercent": match.max_percent,
                "minimumHealthyPercent": match.min_percent,
            },
        }

        grace = match.health_check_grace_sec
        if grace is not None:
            conf["health-check-grace-period-seconds"] = grace

        cli("ecs update-service", conf)
        echo(f"Service updated: {service_name}")

    def remove_service(self, cluster_id, service_name):
        if self.dry_run:
            echo(f"Would have removed service {service_name}")
            return

        echo(f"Removing service: {service_name}")

        cli(
            "ecs update-service",
            {
                "desired-count": 0,
                "service": service_name,
                "cluster": cluster_id,
            },
        )
        deleted = cli(
            "ecs delete-service",
            {
                "service": service_name,
                "cluster": cluster_id,
            },
        )
        echo(f"Service removed: {service_name}")

        t = deleted["service"]["taskDefinition"].split("/")[-1]
        cli(
            "ecs deregister-task-definition",
            {"task-definition": t},
        )
        echo(f"De-registered task definition {t}")

        echo(f"Wait until service terminates: {service_name}")
        cli(
            "ecs wait services-inactive",
            {
                "cluster": cluster_id,
                "service": service_name,
            },
            raise_on_error=False,
            parse_output=False,
        )

    def delete_inactive_ecs_task_definitions(self):
        inactive_tasks = cli(
            "ecs list-task-definitions",
            {"status": "INACTIVE"},
        )["taskDefinitionArns"]
        echo(
            f"Cleaning up inactive ECS tasks definitions. Definitions to delete: {len(inactive_tasks)}",
        )
        chunk_size = 10  # aws API allows to delete up to 10 tasks at once
        for i in range(0, len(inactive_tasks), chunk_size):
            tasks_to_delete = " ".join(inactive_tasks[i : i + chunk_size])
            if self.dry_run:
                echo(f"Would have deleted task definitions: {tasks_to_delete}")
                continue
            cli(
                "ecs delete-task-definitions",
                {"task-definitions": tasks_to_delete},
                print_cmd=True,
            )


def get_all_ecs_tasks(cluster):
    task_arns = []

    def grouper(n, iterable):
        iterable = iter(iterable)
        return iter(lambda: list(itertools.islice(iterable, n)), [])

    for status in ["RUNNING", "STOPPED"]:
        next_token = None
        while True:
            conf = {
                "cluster": cluster,
                "desired-status": status,
            }
            if next_token:
                conf["next-token"] = next_token
            result = cli("ecs list-tasks", conf)
            next_token = result.get("nextToken")
            task_arns += result["taskArns"]
            if not next_token:
                break
    tasks = []
    for arns_chunk in grouper(100, task_arns):
        tasks += cli(
            "ecs describe-tasks",
            {"tasks": " ".join(arns_chunk), "cluster": cluster},
        )["tasks"]
    return tasks


def get_ecs_status(stack_name, services, threads=8):
    desired_services = {s.name: s for s in services}
    clusters = {}

    def split_task_def(task_def):
        return task_def.rsplit(":", 1)

    def fetch_active_task_definitions(service) -> tuple:
        """
        Returns task definition with last revision number and its service
        """
        c = service.cluster_name
        result = cli(
            "ecs list-task-definitions",
            {
                "family-prefix": service.task.family,
                "max-item": 1,
                "sort": "desc",
            },
        )
        task_def, actual_version = split_task_def(
            result["taskDefinitionArns"][0],
        )
        if c not in clusters:
            # physical_name take some time, do not use setdefault
            clusters[c] = physical_name(stack_name, c)
        return task_def, (actual_version, service)

    # use threadpool to fetch results in parallel, much faster
    pool = ThreadPool(processes=threads)
    task_definitions_info = dict(
        pool.map(fetch_active_task_definitions, desired_services.values()),
    )

    number_of_working_actual_tasks = defaultdict(int)
    number_of_working_old_tasks = defaultdict(int)

    stopped_tasks = []
    for cluster in clusters.values():
        tasks = get_all_ecs_tasks(cluster)
        for task in tasks:
            task_def, version = split_task_def(task["taskDefinitionArn"])
            if task_def not in task_definitions_info:
                continue

            actual_version, service = task_definitions_info[task_def]
            status = task["lastStatus"]
            stopped_reason = task.get("stoppedReason", "")

            if task["lastStatus"] == "RUNNING":
                if actual_version == version:
                    number_of_working_actual_tasks[service.name] += 1
                else:
                    number_of_working_old_tasks[service.name] += 1
            elif (
                status == "STOPPED"
                and "Scaling activity initiated" not in stopped_reason
                and task_def in task_definitions_info
            ):
                if actual_version == version:
                    stopped_tasks.append(task)

    for service in desired_services.values():
        service.actual_running_count = number_of_working_actual_tasks.get(service.name, 0)
        service.old_running_count = number_of_working_old_tasks.get(service.name, 0)

    return {
        "services": list(desired_services.values()),
        "stopped_tasks": stopped_tasks,
    }


def monitor_ecs_cluster(stack_name, services, limit_minutes):
    tries = 300
    services = [s for s in services if s.count]

    start = datetime.now()
    notified_done_services = set()
    failed_health_checks = {
        s.name: {"max": s.health_check_failed_count, "count": 0}
        for s in services
        if s.health_check_failed_count is not None
    }

    for i in range(1, tries):
        if (datetime.now() - start).seconds > 60 * limit_minutes:
            raise TimeoutError(f"Not steady for {limit_minutes} minutes")
        echo(f"[{datetime.now().isoformat()}] Try {i}...")
        status = get_ecs_status(stack_name=stack_name, services=services)
        stopped_tasks = [t for t in status["stopped_tasks"] if datetime.fromtimestamp(t["stoppingAt"]) > start]

        if stopped_tasks:
            stop_monitoring = False
            for t in stopped_tasks:
                stopped_reason = t.get("stoppedReason")
                is_elb_error = "Task failed ELB health checks" in stopped_reason
                service_name = t["group"].lstrip("service:")
                if service_name in failed_health_checks and is_elb_error:
                    # Task stopped due to ELB health check error.
                    checks = failed_health_checks[service_name]
                    checks["count"] += 1
                    if checks["count"] > checks["max"]:
                        # The task has run out of attempts.
                        describe_failed_task(t)
                        stop_monitoring = True
                    else:
                        describe_failed_task(t, "WARNING")
                else:
                    # Task stopped for an unknown reasons.
                    describe_failed_task(t)
                    stop_monitoring = True
            if stop_monitoring:
                raise RuntimeError("Tasks stopped unexpectedly")

        incomplete_services = []
        for s in status["services"]:
            if s.count != s.actual_running_count or s.old_running_count:
                incomplete_services.append(s)
            elif s.name not in notified_done_services:
                echo(
                    f"[DONE] Service: {s.name}, "
                    f"desired count: {s.count}, "
                    f"running count: {s.actual_running_count}, "
                    f"old running count: {s.old_running_count}",
                )
                notified_done_services.add(s.name)

        if not incomplete_services:
            break

        for s in incomplete_services:
            echo(
                f"[IN PROGRESS] Service: {s.name}, "
                f"desired count: {s.count}, "
                f"actual running count: {s.actual_running_count}, "
                f"old running count: {s.old_running_count}",
            )
        time.sleep(10)
    else:
        raise TimeoutError(f"Not steady for {tries} tries")
    echo("Done")


def describe_failed_task(task, severity: str = "FAILED"):
    region = task["taskArn"].split(":")[3]
    cluster = task["clusterArn"].split("/")[-1]
    task_id = task["taskArn"].split("/")[-1]
    domain = "console.aws.amazon.com"
    if "us-gov" in region:
        domain = "console.amazonaws-us-gov.com"
    echo(
        f'[{severity}] {task["taskDefinitionArn"]}, '
        f'stopped reason: {task.get("stoppedReason")}, '
        f'exit code:{task["containers"][0].get("exitCode")}, '
        f'status reason:{task["containers"][0].get("reason")}',
    )
    echo(
        f"More info at: "
        f"https://{domain}/ecs/home?"
        f"region={region}#/clusters/{cluster}/tasks/{task_id}"
        f"/details\n",
    )
