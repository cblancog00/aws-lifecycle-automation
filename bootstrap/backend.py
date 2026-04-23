"""
Backend remoto de Terraform: crea el bucket S3 (almacenamiento de estado) y la
tabla DynamoDB (bloqueo de estado) que Terraform necesita antes de poder
gestionar cualquier infraestructura.

Todas las operaciones son idempotentes: volver a ejecutar este módulo contra
una cuenta ya inicializada es seguro y no produce ningún cambio.
"""

from __future__ import annotations

import json
import logging

import boto3
from botocore.exceptions import ClientError

from config import BootstrapConfig

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Bucket S3 de estado                                                          #
# --------------------------------------------------------------------------- #


def _bucket_exists(s3_client, bucket_name: str) -> bool:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            return False
        raise


def _create_bucket(s3_client, bucket_name: str, region: str) -> None:
    """Crea el bucket S3 gestionando la particularidad de LocationConstraint en us-east-1."""
    if region == "us-east-1":
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
    logger.info("Created S3 bucket '%s'.", bucket_name)


def _configure_bucket(s3_client, bucket_name: str) -> None:
    """Aplica la configuración de seguridad y versionado a un bucket existente."""

    # Bloquear todo acceso público
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )

    # Habilitar versionado para que cada revisión del estado sea recuperable
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={"Status": "Enabled"},
    )

    # Forzar cifrado en reposo del lado del servidor (AES-256)
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
                    "BucketKeyEnabled": True,
                },
            ],
        },
    )

    # Denegar cualquier petición que no utilice TLS
    tls_deny_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyInsecureTransport",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
                "Condition": {"Bool": {"aws:SecureTransport": "false"}},
            },
        ],
    }
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(tls_deny_policy),
    )

    logger.info("Applied security configuration to bucket '%s'.", bucket_name)


def create_tf_state_bucket(config: BootstrapConfig) -> None:
    """Asegura que el bucket S3 de estado de Terraform existe y está correctamente configurado."""
    s3 = boto3.client("s3", region_name=config.aws_region)
    bucket_name = config.tf_state_bucket

    if _bucket_exists(s3, bucket_name):
        logger.info("S3 bucket '%s' already exists – skipping creation.", bucket_name)
    else:
        _create_bucket(s3, bucket_name, config.aws_region)

    # Siempre reaplicar la configuración (idempotente, protege contra cambios manuales)
    _configure_bucket(s3, bucket_name)


# --------------------------------------------------------------------------- #
# Tabla de bloqueo DynamoDB                                                    #
# --------------------------------------------------------------------------- #


def _table_exists(dynamodb_client, table_name: str) -> bool:
    try:
        dynamodb_client.describe_table(TableName=table_name)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise


def create_tf_lock_table(config: BootstrapConfig) -> None:
    """Asegura que la tabla DynamoDB de bloqueo de estado existe y está activa."""
    dynamodb = boto3.client("dynamodb", region_name=config.aws_region)
    table_name = config.tf_lock_table

    if _table_exists(dynamodb, table_name):
        logger.info("DynamoDB table '%s' already exists – skipping creation.", table_name)
    else:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "LockID", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "LockID", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
            SSESpecification={"Enabled": True},
            Tags=[
                {"Key": "Project", "Value": "aws-lifecycle-automation"},
                {"Key": "Environment", "Value": config.environment},
                {"Key": "ManagedBy", "Value": "bootstrap"},
            ],
        )
        logger.info("Created DynamoDB table '%s'.", table_name)

    # Esperar hasta que la tabla esté en estado ACTIVE antes de continuar
    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=table_name, WaiterConfig={"Delay": 5, "MaxAttempts": 20})
    logger.info("DynamoDB table '%s' is active.", table_name)
