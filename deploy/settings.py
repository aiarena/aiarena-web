import os
from pathlib import Path

from .ecs import DYNAMIC_PORT, Service, Task
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
AWS_ELB_HEALTH_CHECK_ENDPOINT = "/health-check/"

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
    default_cluster_name = "ECSCluster"


class WebService(BaseService):
    default_role_name = "ECSServiceRole"
    default_min_percent = 50
    default_max_percent = 200


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
    default_memory = 310

    # noinspection PyUnusedLocal
    def nginx_container(self, env, ports, code_containers, name="nginx", command=None, hostname=None):
        return {
            "name": name,
            "cpu": 64,
            "environment": [],
            "essential": True,
            "image": "fholzer/nginx-brotli:v1.21.6",
            "links": code_containers,
            "memory": 32,
            "mountPoints": [
                {
                    "containerPath": volume["host"]["sourcePath"],
                    "readOnly": False,
                    "sourceVolume": volume["name"],
                }
                for volume in (self.volumes or [])
            ],
            "volumesFrom": [{"sourceContainer": container, "readOnly": False} for container in code_containers],
            "hostname": hostname or name,
            "portMappings": ports,
            "entryPoint": ["/bin/sh", "-c"],
            "command": command.split(" "),
        }

    def code_container(self, env, ports, name="code", command=None, hostname=None):
        config = super().code_container(
            env,
            ports,
            name=name,
            command=command,
            hostname=hostname,
        )
        config["logConfiguration"] = {
            "logDriver": "json-file",
            "options": {
                "max-size": "100m",
                "max-file": "3",
            },
        }
        return config

    def containers(self, env, ports):
        return [
            self.code_container(
                env,
                (),
                name=UWSGI_CONTAINER_NAME,
                command="/code/uwsgi.sh",
                hostname=UWSGI_CONTAINER_NAME,
            ),
            self.nginx_container(
                env,
                ports,
                code_containers=[UWSGI_CONTAINER_NAME],
                name="nginx",
                command="/code/nginx.sh",
            ),
        ]


SERVICES = [
    WebService(
        name="webService",
        count=4,
        task=WebTask(
            family="websiteTask",
            ports=[(DYNAMIC_PORT, WEB_PORT)],
            command="",
            cpu=64,  # + 64 nginx = 128
        ),
        container_port=WEB_PORT,
        container_name="nginx",
        health_check_grace_sec=120,
        health_check_failed_count=2,
    ),
]