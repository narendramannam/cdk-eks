#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_eks.cdk_eks_stack import CdkEksStack
from libs.cdk_custom_controller import CustomResourceStack
from libs.cdk_helm_installer import HelmChartStack
from libs.cdk_sm_stack import SSMParameterStack
from libs.logger import create_logger
from libs.yaml_validator import load_and_validate_yaml

logger = create_logger(__name__)

app = cdk.App()
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)
EKS_ADMIN = ""

yaml_file_path = "cluster_config.yaml"
config = load_and_validate_yaml(yaml_file_path)

if config:
    env_path = config["controllers"][0]["env_param_path"]
    environment = config["env"]
    cluster_name = config["clusterName"]
    cluster_version = config["clusterVersion"]
    addons = config["addons"]
    network_name = config["networkName"]

    logger.info("Creating EKS cluster and installing ingress-nginx controller")

    SSMParameterStack(
        app,
        "ssm-cdk-env",
        env_path=env_path,
        environment=environment,
        env=env,
    )

    custom_resource_stack = CustomResourceStack(
        app,
        "nginx-replica-generator",
        env_path=env_path,
        env=env,
    )

    cluster = CdkEksStack(
        app,
        "eks-cdk-demo",
        cluster_name=config["clusterName"],
        cluster_version=cluster_version,
        addons=config["addons"],
        network_name=config["networkName"],
        admin_user=EKS_ADMIN,
        env=env,
    )

    HelmChartStack(
        app,
        "ingress-nginx",
        custom_resource=custom_resource_stack.custom_resource,
        cluster_name=cluster.name,
        master_role=cluster.master_role,
        controllers=config["controllers"],
        env=env,
    )
else:
    logger.error("Failed to validate cluster configuration. Exiting..")

app.synth()
