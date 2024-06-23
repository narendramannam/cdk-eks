import aws_cdk as core
import aws_cdk.assertions as assertions

from app import env, env_path
from libs.cdk_custom_controller import CustomResourceStack


def test_ssm_stack():
    app = core.App()

    custom_resource_stack = CustomResourceStack(
        app,
        "nginx-replica-generator",
        env_path=env_path,
        env=env,
    )

    template = assertions.Template.from_stack(custom_resource_stack)

    template.has_resource_properties("AWS::Lambda::Function", {})
    template.resource_count_is("AWS::CloudFormation::CustomResource", 1)

    template.has_output(
        "ReplicaCount", {"Value": {"Fn::GetAtt": ["CustomResource", "ReplicaCount"]}}
    )
