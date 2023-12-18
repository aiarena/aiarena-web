import os
from pathlib import Path

from .ecs import Service, Task
from .utils import str_to_bool


PROJECT_NAME = "aiarena"

PROJECT_PATH = Path(__file__).parent.parent

PROJECT_ID = 83

WEB_PORT = PROJECT_ID * 100 + 1

IMAGES: dict[str, Path] = {
    "env": PROJECT_PATH / "docker/Dockerfile",
    "cloud": PROJECT_PATH / "docker/Dockerfile_cloud",
    "dev": PROJECT_PATH / "docker/Dockerfile_dev",
}

UWSGI_CONTAINER_NAME = "aiarena-uwsgi"

DB_NAME = "aiarena"
PRODUCTION_DB_USER = "aiarena"
PRODUCTION_DB_ROOT_USER = "aiarena"

AWS_REGION = "eu-central-1"

AWS_ACCOUNT_ID = "315513665747"

# Endpoint used by an ELB target group health checker.
AWS_ELB_HEALTH_CHECK_ENDPOINT = "/health-check/"

PRIVATE_REGISTRY_URL = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"

# Change this in Actions variables
MAINTENANCE_MODE = str_to_bool(os.environ.get("MAINTENANCE_MODE", "False"))

# Enable "Container Insights" for the ECS cluster.
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html
CONTAINER_INSIGHTS = True


class BaseService(Service):
    """
    Service with defaults for this project
    """

    name_prefix = "%s-" % PROJECT_NAME
    launch_type = "FARGATE"
    default_cluster_name = "ECSCluster"
    default_placement_strategy = []
    default_placement_constraints = []


class WebService(BaseService):
    default_min_percent = 100
    default_max_percent = 200
    add_network_configuration = True


class WorkerService(BaseService):
    default_min_percent = 0
    default_max_percent = 200
    default_role_name = None
    add_network_configuration = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if MAINTENANCE_MODE:
            self.count = 0


image_url = f"{PRIVATE_REGISTRY_URL}/{PROJECT_NAME}/{{image}}:latest"


class BaseTask(Task):
    """
    Task with defaults for this project
    """

    family_prefix = "%s-" % PROJECT_NAME
    default_image = image_url.format(image="cloud")


class WebTask(BaseTask):
    default_cpu = "512"
    default_memory = "1024"

    def code_container(self, *args, **kwargs):
        container = super().code_container(*args, **kwargs)
        container["logConfiguration"] = {
            "logDriver": "awslogs",
            "options": {
                "awslogs-create-group": "true",
                "awslogs-group": f"awslogs-{self.family}",
                "awslogs-region": AWS_REGION,
                "awslogs-stream-prefix": f"awslogs-{self.family}",
            },
        }
        return container

    def containers(self, env, ports):
        return [
            self.code_container(
                env,
                ports,
                name=UWSGI_CONTAINER_NAME,
                command="unitd --no-daemon --control unix:/var/run/control.unit.sock",
                entrypoint="/usr/local/bin/docker-entrypoint.sh",
            ),
        ]


class CeleryTask(BaseTask):
    command_prefix = "/bin/bash /app/aiarena/celery.sh -A aiarena "
    default_cpu = "256"
    default_memory = "512"

    def code_container(self, *args, **kwargs):
        config = super().code_container(*args, **kwargs)
        config["logConfiguration"] = {
            "logDriver": "awslogs",
            "options": {
                "awslogs-create-group": "true",
                "awslogs-group": f"awslogs-{self.family}",
                "awslogs-region": AWS_REGION,
                "awslogs-stream-prefix": f"awslogs-{self.family}",
            },
        }
        config["stopTimeout"] = 120
        return config


class CeleryWorkerTask(CeleryTask):
    command_prefix = "/bin/bash /app/aiarena/worker.sh -A aiarena worker -E -l INFO "


SERVICES = [
    WebService(
        name="webService",
        count=2,
        task=WebTask(
            family="websiteTask",
            ports=[(WEB_PORT, WEB_PORT)],
            command="",
        ),
        container_port=WEB_PORT,
        container_name=UWSGI_CONTAINER_NAME,
        health_check_grace_sec=120,
        health_check_failed_count=2,
    ),
    WorkerService(
        name="celeryWorker-Default",
        count=0,
        task=CeleryWorkerTask(
            family="celeryWorker-Default",
            command="-P prefork -Q default",
        ),
    ),
    WorkerService(
        name="celeryBeat",
        count=0,
        task=CeleryTask(
            family="celeryBeat",
            command="beat --loglevel=INFO -s /tmp/celerybeat-schedule --pidfile=",
        ),
    ),
]
