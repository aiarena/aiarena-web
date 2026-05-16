from pydantic import BaseModel, Field

from .session import get_boto3_session
from .settings import PROJECT_NAME


class StackOutputs(BaseModel):
    ecs_cluster: str = Field(alias="EcsCluster")
    ecs_task_role_arn: str = Field(alias="EcsTaskRoleArn")
    ecs_task_execution_role_arn: str = Field(alias="EcsTaskExecutionRoleArn")
    ecs_service_role_arn: str = Field(alias="EcsServiceRoleArn")

    public_subnet_zone_a: str = Field(alias="PublicSubnetZoneA")
    public_subnet_zone_b: str = Field(alias="PublicSubnetZoneB")
    ecs_task_security_group: str = Field(alias="EcsTaskSecurityGroup")

    alb_webserver_target_group_arn: str = Field(alias="AlbWebServerTargetGroupArn")

    main_db_endpoint: str = Field(alias="MainDbEndpoint")
    redis_endpoint: str = Field(alias="RedisEndpoint")

    ecr_repository_cloud_uri: str = Field(alias="EcrRepositoryCloudUri")
    media_production_bucket: str = Field(alias="MediaProductionBucket")
    backups_bucket: str = Field(alias="BackupsBucket")


def fetch_stack_outputs(stack_name: str = PROJECT_NAME, session=None) -> StackOutputs:
    if session is None:
        session = get_boto3_session()
    cfn = session.client("cloudformation")
    response = cfn.describe_stacks(StackName=stack_name)
    outputs = {o["OutputKey"]: o["OutputValue"] for o in response["Stacks"][0]["Outputs"]}
    return StackOutputs.model_validate(outputs)
