import os
from pathlib import Path

from .ecs import Service, Task
from .utils import str_to_bool


PROJECT_NAME = "aiarena"

PROJECT_PATH = Path(__file__).parent.parent

PROJECT_ID = 83

WEB_PORT = PROJECT_ID * 100 + 1
SYSLOG_PORT = 42185

IMAGES: dict[str, Path] = {
    "env": PROJECT_PATH / "docker/Dockerfile",
    "cloud": PROJECT_PATH / "docker/Dockerfile_cloud",
    "dev": PROJECT_PATH / "docker/Dockerfile_dev",
}

UWSGI_CONTAINER_NAME = "aiarena-uwsgi"

DB_NAME = "aiarena"
PRODUCTION_DB_USER = "aiarena"
PRODUCTION_DB_ROOT_USER = "aiarena"

SECRETS_FOLDER = "secrets"

AWS_REGION = "eu-central-1"

AWS_ACCOUNT_ID = "315513665747"

# Endpoint used by an ELB target group health checker.
AWS_ELB_HEALTH_CHECK_ENDPOINT = "/"

PRIVATE_REGISTRY_URL = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com"

FLUENT_HOST = "172.17.0.1"
FLUENT_PORT = "24224"

# Change this in Actions variables
# https://github.com/Perceptive-Care-Systems/app/settings/variables/actions
MAINTENANCE_MODE = str_to_bool(os.environ.get("MAINTENANCE_MODE", "False"))

# Enable "Container Insights" for the ECS cluster.
# https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html
CONTAINER_INSIGHTS = False


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
    default_min_percent = 50
    default_max_percent = 200
    add_network_configuration = True


class WorkerService(BaseService):
    default_min_percent = 0
    default_max_percent = 150

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
                command="/app/aiarena/uwsgi.sh",
            ),
        ]


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
]
