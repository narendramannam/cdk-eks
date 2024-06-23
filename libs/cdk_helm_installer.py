from aws_cdk import CustomResource, Stack
from aws_cdk import aws_eks as eks
from constructs import Construct


class HelmChartStack(Stack):

    def __init__(
        self,
        scope: Construct,
        id: str,
        custom_resource: CustomResource,
        cluster_name: str,
        master_role: str,
        controllers: list,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        replica_count = custom_resource.get_att_string("ReplicaCount")
        helm_values = {"controller": {"replicaCount": replica_count}}

        cluster = eks.Cluster.from_cluster_attributes(
            self,
            "eks-cdk-demo",
            cluster_name=cluster_name,
            kubectl_role_arn=master_role,
        )

        for controller in controllers:
            cluster.add_helm_chart(
                "NginxChart",
                chart=controller["name"],
                release=controller["name"],
                repository="https://kubernetes.github.io/ingress-nginx",  # scope to improve this with controller inventory or a library that can query and return
                namespace=controller["name"],
                values=helm_values,
            )
