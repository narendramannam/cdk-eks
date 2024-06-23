from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SSMParameterStack(Stack):

    def __init__(
        self, scope: Construct, id: str, env_path: str, environment: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        ssm.StringParameter(
            self,
            "NginxEnvironmentParameter",
            parameter_name=env_path,
            string_value=environment,
        )
