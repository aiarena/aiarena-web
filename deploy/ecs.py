import re


class Task:
    default_requires_compatibilities = ["FARGATE"]
    family_prefix = ""
    command_prefix = ""
    default_image = None
    default_cpu = "256"
    default_memory = "512"
    role_name = "ECSTaskRole"
    execution_role_name = "ECSTaskExecutionRole"

    def __init__(
        self,
        family,
        command,
        image=None,
        ports=(),
        cpu=None,
        memory=None,
        volumes=None,
        hostname=None,
        requires_compatibilities=None,
    ):
        self.family = self.family_prefix + family
        self.image = image or self.default_image
        assert self.image, "image must be specified"
        self.command = self.command_prefix + command
        self.ports = ports
        self.cpu = cpu or self.default_cpu
        self.memory = memory or self.default_memory
        self.volumes = volumes
        self.command_chunk = command
        self.hostname = hostname
        self.requires_compatibilities = requires_compatibilities or self.default_requires_compatibilities

    def code_container(self, env, ports, name="code", command=None, hostname=None, entrypoint=None):
        task_config = {
            "name": name,
            "essential": True,
            "image": self.image,
            "command": (command or self.command).split(" "),
            "environment": env,
            "portMappings": ports,
            "mountPoints": [
                {
                    "containerPath": volume["host"]["sourcePath"],
                    "readOnly": False,
                    "sourceVolume": volume["name"],
                }
                for volume in (self.volumes or [])
            ],
        }

        if entrypoint:
            task_config["entrypoint"] = entrypoint

        if self.hostname:
            hostname = self.hostname
        elif self.command_chunk:
            regex = re.search(r"[-A-Za-z0-9_]+$", self.command_chunk.split(" ")[0])
            if regex:
                hostname = regex.group(0).replace("_", "-")

        if hostname:
            task_config["hostname"] = hostname

        return task_config

    def containers(self, env, ports):
        return [
            self.code_container(env, ports),
        ]

    def as_dict(self, environment):
        from deploy.aws import physical_name
        from deploy.settings import AWS_ACCOUNT_ID, PROJECT_NAME

        role_arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{physical_name(PROJECT_NAME, self.role_name)}"
        execution_role_arn = (
            f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{physical_name(PROJECT_NAME, self.execution_role_name)}"
        )

        env = [{"name": k, "value": v} for k, v in environment.items()]
        ports = [{"hostPort": host_port, "containerPort": container_port} for (host_port, container_port) in self.ports]
        return {
            "cpu": self.cpu,
            "memory": self.memory,
            "family": self.family,
            "taskRoleArn": role_arn,
            "executionRoleArn": execution_role_arn,
            "containerDefinitions": self.containers(env, ports),
            "volumes": self.volumes or [],
            "requiresCompatibilities": self.requires_compatibilities,
            "networkMode": "awsvpc",
        }


class Service:
    name_prefix = ""
    default_cluster_name = None
    default_role_name = None
    default_min_percent = 100
    default_max_percent = 200
    default_placement_strategy = [
        {"type": "spread", "field": "instanceId"},
    ]
    default_placement_constraints = []
    default_health_check_grace_sec = None
    default_health_check_fail_cnt = None
    add_network_configuration = False
    launch_type = "EC2"

    def __init__(
        self,
        name,
        task,
        cluster_name=None,
        role_name=None,
        container_port=None,
        container_name=None,
        count=1,
        min_percent=None,
        max_percent=None,
        placement_strategy=None,
        placement_constraints=None,
        health_check_grace_sec=None,
        health_check_failed_count=None,
    ):
        assert isinstance(task, Task), "task must be an instance of Task"
        self.name = self.name_prefix + name
        self.cluster_name = cluster_name or self.default_cluster_name
        assert self.cluster_name, "cluster_name must be specified"
        self.role_name = role_name or self.default_role_name
        self.task = task
        self.container_name = container_name
        self.container_port = container_port
        if self.container_port is not None:
            assert self.container_name, "container_name is required when container port is specified"

        else:
            assert not self.role_name, "role_name can be used together with port only"
        self.count = count

        if min_percent is None:
            self.min_percent = self.default_min_percent
        else:
            self.min_percent = min_percent
        assert isinstance(self.min_percent, int), "min_percent must be an int"

        if max_percent is None:
            self.max_percent = self.default_max_percent
        else:
            self.max_percent = max_percent
        assert isinstance(self.max_percent, int), "max_percent must be an int"

        if placement_strategy is None:
            self.placement_strategy = self.default_placement_strategy
        else:
            self.placement_strategy = placement_strategy
        assert isinstance(self.placement_strategy, list | tuple), "placement_strategy must be a list"

        if placement_constraints is None:
            self.placement_constraints = self.default_placement_constraints
        else:
            self.placement_constraints = placement_constraints
        assert isinstance(self.placement_constraints, list | tuple), "placement_constraints must be a list"

        if self.launch_type == "FARGATE":
            assert not self.placement_strategy, "placement_strategy doesn't work with FARGATE"
            assert not self.placement_constraints, "placement_constraints doesn't work with FARGATE"

        self.health_check_grace_sec = health_check_grace_sec
        if self.health_check_grace_sec is None:
            self.health_check_grace_sec = self.default_health_check_grace_sec
        if self.health_check_grace_sec is not None:
            value = self.health_check_grace_sec
            assert isinstance(value, int), f"health_check_grace_sec must be an int, got: {type(value)}"
            assert self.health_check_grace_sec >= 0, f"health_check_grace_sec cant be negative, got: {value}"

        self.health_check_failed_count = health_check_failed_count
        if self.health_check_failed_count is None:
            self.health_check_failed_count = self.default_health_check_fail_cnt
        if self.health_check_failed_count is not None:
            value = self.health_check_failed_count
            assert isinstance(value, int), f"health_check_failed_count must be an int, got: {type(value)}"
            assert self.health_check_failed_count >= 0, f"health_check_failed_count cant be negative, got: {value}"
