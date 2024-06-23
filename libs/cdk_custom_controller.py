from aws_cdk import CfnOutput, CustomResource, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import custom_resources as cr
from constructs import Construct


class CustomResourceStack(Stack):

    def __init__(self, scope: Construct, id: str, env_path: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lambda_function = _lambda.Function(
            self,
            "NginxReplicaCount",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="value_issuer.handler",
            code=_lambda.Code.from_asset("lambda"),
        )

        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{env_path}"
                ],
            )
        )

        provider = cr.Provider(
            self, "GenerateIgninxHelmValues", on_event_handler=lambda_function
        )

        self.custom_resource = CustomResource(
            self, "CustomResource", service_token=provider.service_token
        )

        CfnOutput(
            self,
            "ReplicaCount",
            value=self.custom_resource.get_att_string("ReplicaCount"),
        )
