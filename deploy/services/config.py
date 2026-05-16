"""Service definitions for the production ECS deployment.

Translates project config into the typed `ecs_deployer_boto3` Service/Task
shape that `ApplicationUpdater` and `DeploymentMonitor` consume.
"""

from ecs_deployer_boto3 import (
    AwsVpcConfiguration,
    CapacityProviderStrategyItem,
    Container,
    DeploymentConfiguration,
    LinuxParameters,
    LoadBalancer,
    LogConfiguration,
    NetworkConfiguration,
    PortMapping,
    Service,
    Task,
    VolumeFrom,
)

from deploy.settings import (
    AWS_REGION,
    DJANGO_PORT,
    MAINTENANCE_MODE,
    NGINX_CONTAINER_NAME,
    PROJECT_NAME,
    UWSGI_CONTAINER_NAME,
    WEB_PORT,
)
from deploy.stack_outputs import StackOutputs


CLOUD_IMAGE_TAG = "latest"
NGINX_IMAGE = "fholzer/nginx-brotli:v1.26.2"

CAPACITY_PROVIDER_STRATEGY = [
    CapacityProviderStrategyItem(capacity_provider="FARGATE_SPOT", weight=1),
]


def _awslogs(family: str, suffix: str) -> LogConfiguration:
    # Preserves the existing log-group-per-(family, container) scheme so
    # historical CloudWatch state stays queryable.
    return LogConfiguration(
        log_driver="awslogs",
        options={
            "awslogs-create-group": "true",
            "awslogs-group": f"awslogs-{family}-{suffix}",
            "awslogs-region": AWS_REGION,
            "awslogs-stream-prefix": f"awslogs-{family}",
        },
    )


def _network_configuration(stack_outputs: StackOutputs) -> NetworkConfiguration:
    return NetworkConfiguration(
        awsvpc_configuration=AwsVpcConfiguration(
            subnets=[
                stack_outputs.public_subnet_zone_a,
                stack_outputs.public_subnet_zone_b,
            ],
            security_groups=[stack_outputs.ecs_task_security_group],
            assign_public_ip="ENABLED",
        ),
    )


def get_services(stack_outputs: StackOutputs) -> list[Service]:
    cloud_image = f"{stack_outputs.ecr_repository_cloud_uri}:{CLOUD_IMAGE_TAG}"
    network_configuration = _network_configuration(stack_outputs)

    def task(family: str, containers: list[Container], cpu: str, memory: str) -> Task:
        return Task(
            family=f"{PROJECT_NAME}-{family}",
            containers=containers,
            cpu=cpu,
            memory=memory,
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            task_role_arn=stack_outputs.ecs_task_role_arn,
            execution_role_arn=stack_outputs.ecs_task_execution_role_arn,
        )

    web_family = f"{PROJECT_NAME}-websiteTask"
    web_task = task(
        family="websiteTask",
        cpu="256",
        memory="1024",
        containers=[
            Container(
                name=UWSGI_CONTAINER_NAME,
                image=cloud_image,
                command=["/app/aiarena/uwsgi.sh"],
                port_mappings=[PortMapping(container_port=DJANGO_PORT, host_port=DJANGO_PORT)],
                log_configuration=_awslogs(web_family, "django"),
            ),
            Container(
                name=NGINX_CONTAINER_NAME,
                image=NGINX_IMAGE,
                entry_point=["/bin/sh", "-c"],
                command=["/app/aiarena/nginx.sh"],
                port_mappings=[PortMapping(container_port=WEB_PORT, host_port=WEB_PORT)],
                volumes_from=[VolumeFrom(source_container=UWSGI_CONTAINER_NAME)],
                linux_parameters=LinuxParameters(init_process_enabled=True),
                log_configuration=_awslogs(web_family, "nginx"),
            ),
        ],
    )

    def celery_container(family: str, command: list[str]) -> Container:
        return Container(
            name="code",
            image=cloud_image,
            command=command,
            log_configuration=_awslogs(f"{PROJECT_NAME}-{family}", "celery"),
            stop_timeout=120,
        )

    def celery_worker_command(queue_args: str) -> list[str]:
        return [
            "/bin/bash",
            "/app/aiarena/worker.sh",
            "-A",
            "aiarena",
            "worker",
            "-E",
            "-l",
            "INFO",
            *queue_args.split(" "),
        ]

    celery_beat_command = [
        "/bin/bash",
        "/app/aiarena/celery.sh",
        "-A",
        "aiarena",
        "beat",
        "--loglevel=INFO",
        "-s",
        "/tmp/celerybeat-schedule",
        "--pidfile=",
    ]

    worker_deployment = DeploymentConfiguration(
        strategy="ROLLING",
        minimum_healthy_percent=0,
        maximum_percent=200,
    )
    worker_count = 0 if MAINTENANCE_MODE else 1

    return [
        Service(
            name=f"{PROJECT_NAME}-webService",
            cluster=stack_outputs.ecs_cluster,
            task_definition=web_task,
            desired_count=4,
            capacity_provider_strategy=CAPACITY_PROVIDER_STRATEGY,
            deployment_configuration=DeploymentConfiguration(
                strategy="ROLLING",
                minimum_healthy_percent=100,
                maximum_percent=200,
            ),
            load_balancers=[
                LoadBalancer(
                    target_group_arn=stack_outputs.alb_webserver_target_group_arn,
                    container_name=NGINX_CONTAINER_NAME,
                    container_port=WEB_PORT,
                ),
            ],
            network_configuration=network_configuration,
            health_check_grace_period_seconds=120,
            deploy_monitoring_health_check_failed_count=2,
            enable_execute_command=True,
        ),
        Service(
            name=f"{PROJECT_NAME}-celeryWorker-Default",
            cluster=stack_outputs.ecs_cluster,
            task_definition=task(
                family="celeryWorker-Default",
                cpu="256",
                memory="512",
                containers=[
                    celery_container(
                        "celeryWorker-Default",
                        celery_worker_command("--concurrency 1 -P solo -Q default"),
                    ),
                ],
            ),
            desired_count=worker_count,
            capacity_provider_strategy=CAPACITY_PROVIDER_STRATEGY,
            deployment_configuration=worker_deployment,
            network_configuration=network_configuration,
            enable_execute_command=True,
        ),
        Service(
            name=f"{PROJECT_NAME}-celeryWorker-Monitoring",
            cluster=stack_outputs.ecs_cluster,
            task_definition=task(
                family="celeryWorker-Monitoring",
                cpu="256",
                memory="512",
                containers=[
                    celery_container(
                        "celeryWorker-Monitoring",
                        celery_worker_command("--concurrency 1 -P solo -Q monitoring"),
                    ),
                ],
            ),
            desired_count=worker_count,
            capacity_provider_strategy=CAPACITY_PROVIDER_STRATEGY,
            deployment_configuration=worker_deployment,
            network_configuration=network_configuration,
            enable_execute_command=True,
        ),
        Service(
            name=f"{PROJECT_NAME}-celeryBeat",
            cluster=stack_outputs.ecs_cluster,
            task_definition=task(
                family="celeryBeat",
                cpu="256",
                memory="512",
                containers=[celery_container("celeryBeat", celery_beat_command)],
            ),
            desired_count=worker_count,
            capacity_provider_strategy=CAPACITY_PROVIDER_STRATEGY,
            deployment_configuration=worker_deployment,
            network_configuration=network_configuration,
            enable_execute_command=True,
        ),
    ]
