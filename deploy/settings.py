import os
from pathlib import Path

from .utils import str_to_bool


PROJECT_NAME = "aiarena"

PROJECT_PATH = Path(__file__).parent.parent

PROJECT_ID = 83

WEB_PORT = PROJECT_ID * 100 + 1
DJANGO_PORT = PROJECT_ID * 100 + 11

IMAGES: dict[str, Path] = {
    "env": PROJECT_PATH / "docker/Dockerfile",
    "cloud": PROJECT_PATH / "docker/Dockerfile_cloud",
    "dev": PROJECT_PATH / "docker/Dockerfile_dev",
}

UWSGI_CONTAINER_NAME = "aiarena-uwsgi"
NGINX_CONTAINER_NAME = "nginx"

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
CONTAINER_INSIGHTS = False
