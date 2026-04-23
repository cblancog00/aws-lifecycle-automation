"""
IAM: crea el rol y la política de permisos inline que GitHub Actions assume
(vía OIDC) para ejecutar Terraform contra la cuenta de AWS de destino.

Los permisos siguen el principio de mínimo privilegio, limitados a los servicios
utilizados por la aplicación serverless (Lambda, S3, DynamoDB, SQS,
EventBridge Pipes, CloudWatch Logs e IAM para roles de ejecución de Lambda).

Todas las operaciones son idempotentes.
"""

from __future__ import annotations

import json
import logging

import boto3
from botocore.exceptions import ClientError

from config import BootstrapConfig

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Política de confianza                                                        #
# --------------------------------------------------------------------------- #


def _build_trust_policy(config: BootstrapConfig) -> dict:
    """
    Devuelve una política de confianza IAM que permite a GitHub Actions asumir el rol
    únicamente cuando el token OIDC proviene del repositorio configurado.

    La condición 'sub' restringe la confianza al repositorio específico; opcionalmente
    se puede limitar a una rama concreta sustituyendo el comodín por, por ejemplo,
    'repo:org/repo:ref:refs/heads/main'.
    """
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "GitHubActionsOIDC",
                "Effect": "Allow",
                "Principal": {
                    "Federated": config.oidc_provider_arn,
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": config.github_subject,
                    },
                },
            },
        ],
    }


# --------------------------------------------------------------------------- #
# Política de permisos                                                         #
# --------------------------------------------------------------------------- #


def _build_permission_policy(config: BootstrapConfig) -> dict:
    """
    Devuelve una política de permisos IAM que cubre los servicios de AWS que Terraform
    gestionará para la aplicación serverless.

    Los permisos se limitan a la cuenta y al entorno donde es possible.
    'iam:PassRole' se restringe a roles de ejecución de Lambda para evitar
    escalada de privilegios.
    """
    account = config.aws_account_id
    region = config.aws_region
    env = config.environment

    return {
        "Version": "2012-10-17",
        "Statement": [
            # ---------------------------------------------------------------- #
            # Backend de estado de Terraform                                    #
            # ---------------------------------------------------------------- #
            {
                "Sid": "TerraformStateAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                    "s3:GetBucketVersioning",
                    "s3:GetEncryptionConfiguration",
                ],
                "Resource": [
                    f"arn:aws:s3:::{config.tf_state_bucket}",
                    f"arn:aws:s3:::{config.tf_state_bucket}/*",
                ],
            },
            {
                "Sid": "TerraformStateLock",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:DescribeTable",
                ],
                "Resource": (f"arn:aws:dynamodb:{region}:{account}:table/{config.tf_lock_table}"),
            },
            # ---------------------------------------------------------------- #
            # Lambda (cómputo de la aplicación)                                #
            # ---------------------------------------------------------------- #
            {
                "Sid": "LambdaManagement",
                "Effect": "Allow",
                "Action": [
                    "lambda:CreateFunction",
                    "lambda:DeleteFunction",
                    "lambda:GetFunction",
                    "lambda:GetFunctionConfiguration",
                    "lambda:UpdateFunctionCode",
                    "lambda:UpdateFunctionConfiguration",
                    "lambda:PublishVersion",
                    "lambda:CreateAlias",
                    "lambda:DeleteAlias",
                    "lambda:GetAlias",
                    "lambda:UpdateAlias",
                    "lambda:ListVersionsByFunction",
                    "lambda:AddPermission",
                    "lambda:RemovePermission",
                    "lambda:GetPolicy",
                    "lambda:CreateEventSourceMapping",
                    "lambda:DeleteEventSourceMapping",
                    "lambda:GetEventSourceMapping",
                    "lambda:UpdateEventSourceMapping",
                    "lambda:ListTags",
                    "lambda:TagResource",
                    "lambda:UntagResource",
                ],
                "Resource": [
                    f"arn:aws:lambda:{region}:{account}:function:*-{env}-*",
                    f"arn:aws:lambda:{region}:{account}:event-source-mapping:*",
                ],
            },
            # ---------------------------------------------------------------- #
            # S3 (bucket de entrada de la aplicación)                          #
            # ---------------------------------------------------------------- #
            {
                "Sid": "S3AppBucketManagement",
                "Effect": "Allow",
                "Action": [
                    "s3:CreateBucket",
                    "s3:DeleteBucket",
                    "s3:GetBucketLocation",
                    "s3:GetBucketPolicy",
                    "s3:PutBucketPolicy",
                    "s3:DeleteBucketPolicy",
                    "s3:GetBucketVersioning",
                    "s3:PutBucketVersioning",
                    "s3:GetEncryptionConfiguration",
                    "s3:PutEncryptionConfiguration",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:PutBucketPublicAccessBlock",
                    "s3:GetBucketNotification",
                    "s3:PutBucketNotification",
                    "s3:GetBucketTagging",
                    "s3:PutBucketTagging",
                    "s3:ListBucket",
                    "s3:GetLifecycleConfiguration",
                    "s3:PutLifecycleConfiguration",
                ],
                "Resource": f"arn:aws:s3:::*-{env}-*",
            },
            # ---------------------------------------------------------------- #
            # DynamoDB (almacén de datos de la aplicación)                     #
            # ---------------------------------------------------------------- #
            {
                "Sid": "DynamoDBManagement",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:CreateTable",
                    "dynamodb:DeleteTable",
                    "dynamodb:DescribeTable",
                    "dynamodb:UpdateTable",
                    "dynamodb:DescribeTimeToLive",
                    "dynamodb:UpdateTimeToLive",
                    "dynamodb:DescribeContinuousBackups",
                    "dynamodb:UpdateContinuousBackups",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams",
                    "dynamodb:ListTagsOfResource",
                    "dynamodb:TagResource",
                    "dynamodb:UntagResource",
                    "dynamodb:DescribeKinesisStreamingDestination",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{region}:{account}:table/*-{env}-*",
                    f"arn:aws:dynamodb:{region}:{account}:table/*-{env}-*/stream/*",
                ],
            },
            # ---------------------------------------------------------------- #
            # SQS (cola de mensajes fallidos y procesamiento posterior)         #
            # ---------------------------------------------------------------- #
            {
                "Sid": "SQSManagement",
                "Effect": "Allow",
                "Action": [
                    "sqs:CreateQueue",
                    "sqs:DeleteQueue",
                    "sqs:GetQueueAttributes",
                    "sqs:SetQueueAttributes",
                    "sqs:GetQueueUrl",
                    "sqs:ListQueueTags",
                    "sqs:TagQueue",
                    "sqs:UntagQueue",
                ],
                "Resource": f"arn:aws:sqs:{region}:{account}:*-{env}-*",
            },
            # ---------------------------------------------------------------- #
            # EventBridge Pipes                                                 #
            # ---------------------------------------------------------------- #
            {
                "Sid": "EventBridgePipesManagement",
                "Effect": "Allow",
                "Action": [
                    "pipes:CreatePipe",
                    "pipes:DeletePipe",
                    "pipes:DescribePipe",
                    "pipes:UpdatePipe",
                    "pipes:StartPipe",
                    "pipes:StopPipe",
                    "pipes:ListTagsForResource",
                    "pipes:TagResource",
                    "pipes:UntagResource",
                ],
                "Resource": (f"arn:aws:pipes:{region}:{account}:pipe/*-{env}-*"),
            },
            # ---------------------------------------------------------------- #
            # CloudWatch Logs (grupos de logs de Lambda)                        #
            # ---------------------------------------------------------------- #
            {
                "Sid": "CloudWatchLogsManagement",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:DeleteLogGroup",
                    "logs:DescribeLogGroups",
                    "logs:PutRetentionPolicy",
                    "logs:DeleteRetentionPolicy",
                    "logs:ListTagsLogGroup",
                    "logs:TagLogGroup",
                    "logs:UntagLogGroup",
                    "logs:ListTagsForResource",
                    "logs:TagResource",
                    "logs:UntagResource",
                ],
                "Resource": (f"arn:aws:logs:{region}:{account}:log-group:/aws/lambda/*-{env}-*"),
            },
            # ---------------------------------------------------------------- #
            # IAM – sólo roles de ejecución de Lambda (evita escalada de privilegios) #
            # ---------------------------------------------------------------- #
            {
                "Sid": "IAMLambdaRolesManagement",
                "Effect": "Allow",
                "Action": [
                    "iam:CreateRole",
                    "iam:DeleteRole",
                    "iam:GetRole",
                    "iam:UpdateRole",
                    "iam:UpdateAssumeRolePolicy",
                    "iam:AttachRolePolicy",
                    "iam:DetachRolePolicy",
                    "iam:PutRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:GetRolePolicy",
                    "iam:ListRolePolicies",
                    "iam:ListAttachedRolePolicies",
                    "iam:ListInstanceProfilesForRole",
                    "iam:TagRole",
                    "iam:UntagRole",
                ],
                "Resource": (f"arn:aws:iam::{account}:role/*-{env}-lambda-*"),
            },
            {
                "Sid": "IAMPassRoleToLambda",
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": f"arn:aws:iam::{account}:role/*-{env}-lambda-*",
                "Condition": {"StringEquals": {"iam:PassedToService": "lambda.amazonaws.com"}},
            },
            # ---------------------------------------------------------------- #
            # STS – necesario para el proveedor AWS de Terraform               #
            # ---------------------------------------------------------------- #
            {
                "Sid": "STSCallerIdentity",
                "Effect": "Allow",
                "Action": "sts:GetCallerIdentity",
                "Resource": "*",
            },
        ],
    }


# --------------------------------------------------------------------------- #
# Ciclo de vida del rol                                                        #
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


def _role_exists(iam_client, role_name: str) -> bool:
    try:
        iam_client.get_role(RoleName=role_name)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchEntityException":
            return False
        raise


def create_terraform_role(config: BootstrapConfig) -> str:
    """
    Crea (o actualiza) el rol IAM que GitHub Actions assume para ejecutar Terraform.
    Devuelve el ARN del rol.
    """
    iam = boto3.client("iam")
    role_name = config.terraform_role_name
    trust_policy = json.dumps(_build_trust_policy(config))
    permission_policy = json.dumps(_build_permission_policy(config))
    policy_name = f"{role_name}-policy"

    if _role_exists(iam, role_name):
        logger.info("IAM role '%s' already exists – updating policies.", role_name)
        # Actualizar la política de confianza por si ha cambiado el ARN del proveedor OIDC
        iam.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=trust_policy,
        )
    else:
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy,
            Description=(
                f"Assumed by GitHub Actions (OIDC) to run Terraform "
                f"for the {config.environment} environment."
            ),
            MaxSessionDuration=3600,
            Tags=[
                {"Key": "Project", "Value": "aws-lifecycle-automation"},
                {"Key": "Environment", "Value": config.environment},
                {"Key": "ManagedBy", "Value": "bootstrap"},
            ],
        )
        logger.info("Created IAM role '%s'.", role_name)

    # Sobreescribir siempre la política inline para mantenerla sincronizada con este código
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=permission_policy,
    )
    logger.info("Applied inline permission policy to role '%s'.", role_name)

    role_arn: str = iam.get_role(RoleName=role_name)["Role"]["Arn"]
    logger.info("Terraform IAM role ARN: %s", role_arn)
    return role_arn
