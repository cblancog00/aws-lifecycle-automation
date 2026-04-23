"""
Configuración del bootstrap: parsing de argumentos y dataclass de configuración central.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import boto3


@dataclass
class BootstrapConfig:
    """
    Almacena todos los valores de configuración derivados
    de los argumentos CLI y la cuenta de AWS.
    """

    aws_region: str
    aws_account_id: str
    github_org: str
    github_repo: str
    environment: str

    # ------------------------------------------------------------------ #
    # Nombres derivados de recursos                                        #
    # ------------------------------------------------------------------ #

    @property
    def tf_state_bucket(self) -> str:
        """Nombre del bucket S3 para el estado remoto de Terraform."""
        return f"tfstate-{self.aws_account_id}-{self.environment}"

    @property
    def tf_lock_table(self) -> str:
        """Nombre de la tabla DynamoDB para el bloqueo del estado de Terraform."""
        return f"tfstate-lock-{self.environment}"

    @property
    def terraform_role_name(self) -> str:
        """Rol IAM asumido por GitHub Actions para ejecutar operaciones de Terraform."""
        return f"github-actions-terraform-{self.environment}"

    @property
    def oidc_provider_url(self) -> str:
        return "https://token.actions.githubusercontent.com"

    @property
    def oidc_provider_arn(self) -> str:
        return (
            f"arn:aws:iam::{self.aws_account_id}:oidc-provider/token.actions.githubusercontent.com"
        )

    @property
    def github_subject(self) -> str:
        """Claim 'sub' de OIDC que restringe la confianza al repositorio configurado."""
        return f"repo:{self.github_org}/{self.github_repo}:*"


def load_config() -> BootstrapConfig:
    """Parsea los argumentos CLI, resuelve el ID de cuenta de AWS y devuelve un BootstrapConfig."""
    parser = argparse.ArgumentParser(
        description=(
            "Crea los prerrequisitos de AWS necesarios para el estado remoto de Terraform "
            "y la autenticación OIDC de GitHub Actions."
        ),
    )
    parser.add_argument(
        "--region",
        required=True,
        help="Región de AWS donde se crearán los recursos del bootstrap (p. ej. eu-west-1).",
    )
    parser.add_argument(
        "--github-org",
        required=True,
        help="Nombre de la organización o usuario de GitHub propietario del repositorio.",
    )
    parser.add_argument(
        "--github-repo",
        required=True,
        help="Nombre del repositorio de GitHub (sin el prefijo de organización).",
    )
    parser.add_argument(
        "--environment",
        choices=["dev", "prod"],
        default="dev",
        help="Entorno de destino. Controla el nombrado de recursos. Por defecto: dev.",
    )

    args = parser.parse_args()

    sts = boto3.client("sts", region_name=args.region)
    account_id: str = sts.get_caller_identity()["Account"]

    return BootstrapConfig(
        aws_region=args.region,
        aws_account_id=account_id,
        github_org=args.github_org,
        github_repo=args.github_repo,
        environment=args.environment,
    )
