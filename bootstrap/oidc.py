"""
Proveedor de identidad OIDC: registra GitHub Actions como proveedor de identidad
de confianza en AWS IAM para que los flujos de trabajo puedan obtener credenciales
de corta duración mediante 'sts:AssumeRoleWithWebIdentity' sin almacenar secretos
de larga duración.

Referencia:
  https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services

Todas las operaciones son idempotentes.
"""
from __future__ import annotations

import logging

import boto3
from botocore.exceptions import ClientError

from config import BootstrapConfig

logger = logging.getLogger(__name__)

# AWS valida el proveedor OIDC de GitHub utilizando su propia biblioteca de CAs en lugar
# de la lista de thumbprints, por lo que el valor indicado es aceptado pero no verificado
# criptográficamente por AWS. Coincide con la huella SHA-1 de la CA intermedia TLS de
# GitHub y es el valor recomendado en la documentación oficial de GitHub.
# Ver: https://github.blog/changelog/2022-01-13-github-actions-update-on-oidc-based-deployments-to-aws/
_GITHUB_OIDC_THUMBPRINT = "6938fd4d98bab03faadb97b34396831e3780aea1"

_GITHUB_OIDC_URL = "https://token.actions.githubusercontent.com"
_GITHUB_CLIENT_ID = "sts.amazonaws.com"


def _provider_exists(iam_client, provider_arn: str) -> bool:
    try:
        iam_client.get_open_id_connect_provider(OpenIDConnectProviderArn=provider_arn)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchEntityException":
            return False
        raise


def create_oidc_provider(config: BootstrapConfig) -> str:
    """
    Asegura que el proveedor OIDC de GitHub Actions existe en la cuenta de AWS.
    Devuelve el ARN del proveedor.
    """
    iam = boto3.client("iam")
    provider_arn = config.oidc_provider_arn

    if _provider_exists(iam, provider_arn):
        logger.info("OIDC provider already exists: %s", provider_arn)
        return provider_arn

    response = iam.create_open_id_connect_provider(
        Url=_GITHUB_OIDC_URL,
        ClientIDList=[_GITHUB_CLIENT_ID],
        ThumbprintList=[_GITHUB_OIDC_THUMBPRINT],
        Tags=[
            {"Key": "Project", "Value": "aws-lifecycle-automation"},
            {"Key": "ManagedBy", "Value": "bootstrap"},
        ],
    )
    provider_arn = response["OpenIDConnectProviderArn"]
    logger.info("Created OIDC provider: %s", provider_arn)
    return provider_arn
