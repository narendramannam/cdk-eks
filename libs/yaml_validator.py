from typing import Optional

import yaml
from cerberus import Validator

from libs.logger import create_logger

logger = create_logger(__name__)

schema = {
    "clusterName": {"type": "string", "required": True},
    "clusterVersion": {"type": "string", "required": True},
    "region": {"type": "string", "required": True},
    "env": {
        "type": "string",
        "required": True,
        "allowed": ["development", "staging", "production"],
    },
    "addons": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {
                    "type": "string",
                    "required": True,
                    "allowed": ["coredns", "kube-proxy", "vpc-cni"],
                }
            },
        },
        "required": True,
    },
    "networkName": {"type": "string", "required": True},
    "controllers": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "env_param_path": {"type": "string", "required": True},
            },
        },
        "required": True,
    },
}


def load_and_validate_yaml(
    file_path: str, valid_schema: Optional[dict] = schema
) -> Optional[dict]:
    """Validates a cluster YAML input with pre-defined YAML Schema.

    Args:
        file_path: Cluster configuration YAML file.
        valid_schema: an Optional schema input, if not specified default schema is used for validation

    Returns:
        Optionally returns valid YAML data when validation succeeds
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    v = Validator(valid_schema)
    if v.validate(data):
        logger.info("Validating cluster definition YAML successful.")
        return data
    else:
        logger.error("Validating cluster definition YAML failed.")
        logger.error(v.errors)
        return None
