import logging
from typing import Optional

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context) -> Optional[None]:
    ssm = boto3.client("ssm")
    parameter_name = "/platform/account/env"
    try:
        parameter = ssm.get_parameter(
            Name=parameter_name,
        )
        environment = parameter["Parameter"]["Value"]

        if environment == "development":
            replica_count = 1
        elif environment in ["staging", "production"]:
            replica_count = 2
        else:
            raise ValueError(f"Unknown environment: {environment}")

        return {"Data": {"ReplicaCount": replica_count}}
    except ssm.exceptions.ParameterNotFound:
        logger.error(f"SSM parameter {parameter_name} not found")
        raise ValueError(f"SSM parameter {parameter_name} not found")
    except Exception as e:
        logger.error(f"Error retrieving SSM parameter: {str(e)}")
        raise ValueError(f"Error retrieving SSM parameter: {str(e)}")
