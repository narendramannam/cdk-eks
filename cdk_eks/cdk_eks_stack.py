# from aws_cdk import core
from typing import Optional

from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_eks as eks  # Duration,
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from constructs import Construct


class CdkEksStack(Stack):

    @property
    def name(self) -> str:
        return self._cluster.cluster_name

    @property
    def master_role(self) -> str:
        return self._eks_master_role.role_arn

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cluster_name: str,
        cluster_version: str,
        addons: list,
        network_name: str,
        admin_user: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_name=network_name)
        print("This is the vpc ", vpc.vpc_id)
        vpc_subnets = [{"subnetType": ec2.SubnetType.PRIVATE_WITH_NAT}]
        eks_version = eks.KubernetesVersion.of(cluster_version)
        addons_map = {
            "1.30": {
                "coredns": "v1.11.1-eksbuild.9",
                "vpc-cni": "v1.18.2-eksbuild.1",
                "kube-proxy": "v1.30.0-eksbuild.3",
            },
            "1.29": {
                "coredns": "v1.11.1-eksbuild.9",
                "vpc-cni": "v1.18.2-eksbuild.1",
                "kube-proxy": "v1.29.3-eksbuild.5",
            },
        }

        # create eks admin role
        self._eks_master_role = iam.Role(
            self,
            "EksMasterRole",
            role_name="EksAdminRole",
            assumed_by=iam.AccountRootPrincipal(),
        )

        self._secrets_key = kms.Key(self, "EksKms")

        self._cluster = eks.Cluster(
            self,
            "Cluster",
            vpc=vpc,
            version=eks_version,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            masters_role=self._eks_master_role,
            default_capacity=0,
            vpc_subnets=vpc_subnets,
            authentication_mode=eks.AuthenticationMode.API_AND_CONFIG_MAP,
            secrets_encryption_key=self._secrets_key,
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.SCHEDULER,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
            ],
        )

        if admin_user:
            admin_user = iam.User(self, admin_user)
            self._cluster.aws_auth.add_user_mapping(
                admin_user, groups=["system:masters"]
            )

        if addons:
            for addon in addons:
                eks.CfnAddon(
                    self,
                    addon["name"],
                    addon_name=addon["name"],
                    cluster_name=self._cluster.cluster_name,
                    addon_version=addons_map[cluster_version][addon["name"]],
                    preserve_on_delete=False,
                )

        eks_cluster_node_group_role = iam.Role(
            self,
            "eksClusterNodeGroupRole",
            role_name="eksClusterNodeGroupRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEKSWorkerNodePolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ContainerRegistryReadOnly"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKS_CNI_Policy"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
            ],
        )

        self._cluster.add_nodegroup_capacity(
            "managed-node-group",
            instance_types=[
                ec2.InstanceType("m5.large"),
                ec2.InstanceType("t3.large"),
                ec2.InstanceType("t3.xlarge"),
                ec2.InstanceType("t3.medium"),
            ],
            min_size=1,
            max_size=5,
            disk_size=20,
            capacity_type=eks.CapacityType.SPOT,
            ami_type=eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
            node_role=eks_cluster_node_group_role,
        )
