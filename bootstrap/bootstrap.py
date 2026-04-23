"""
Punto de entrada del bootstrap.

Orquesta los tres pasos previous que deben existir antes de que Terraform
pueda gestionar cualquier infraestructura:

  1. Backend remoto de Terraform  – bucket S3 + tabla de bloqueo DynamoDB.
  2. Proveedor de identidad OIDC  – registra GitHub Actions como IdP de confianza.
  3. Rol IAM para Terraform       – rol asumido por GitHub Actions vía OIDC.

Uso:
  uv run bootstrap.py \\
      --region eu-west-1 \\
      --github-org <org> \\
      --github-repo <repo> \\
      [--environment dev|prod]

Tras una ejecución exitosa el script imprime un resumen con los nombres de
recursos y ARNs que deben referenciarse en la configuración del backend de
Terraform y en los ficheros de flujo de trabajo de GitHub Actions.
"""

from __future__ import annotations

import logging
import sys

from backend import create_tf_lock_table, create_tf_state_bucket
from config import load_config
from iam import create_terraform_role
from oidc import create_oidc_provider


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s – %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    _configure_logging()
    logger = logging.getLogger(__name__)

    config = load_config()

    logger.info(
        "Starting bootstrap for environment '%s' in account %s (%s).",
        config.environment,
        config.aws_account_id,
        config.aws_region,
    )

    # ------------------------------------------------------------------ #
    # Paso 1 – Backend remoto de Terraform                                #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 1/3: Terraform remote backend ===")
    create_tf_state_bucket(config)
    create_tf_lock_table(config)

    # ------------------------------------------------------------------ #
    # Paso 2 – Proveedor OIDC de GitHub Actions                          #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 2/3: GitHub Actions OIDC provider ===")
    provider_arn = create_oidc_provider(config)

    # ------------------------------------------------------------------ #
    # Paso 3 – Rol IAM para Terraform                                     #
    # ------------------------------------------------------------------ #
    logger.info("=== Step 3/3: IAM role for Terraform ===")
    role_arn = create_terraform_role(config)

    # ------------------------------------------------------------------ #
    # Resumen                                                             #
    # ------------------------------------------------------------------ #
    separator = "-" * 60
    print(f"\n{separator}")
    print("Bootstrap completed successfully.")
    print(separator)
    print(f"  Environment          : {config.environment}")
    print(f"  AWS account          : {config.aws_account_id}")
    print(f"  Region               : {config.aws_region}")
    print(separator)
    print("Terraform backend configuration:")
    print(f'  bucket               = "{config.tf_state_bucket}"')
    print(f'  key                  = "{config.environment}/terraform.tfstate"')
    print(f'  region               = "{config.aws_region}"')
    print(f'  dynamodb_table       = "{config.tf_lock_table}"')
    print("  encrypt              = true")
    print(separator)
    print("GitHub Actions secrets / variables:")
    print(f"  AWS_REGION           = {config.aws_region}")
    print(f"  AWS_ROLE_ARN         = {role_arn}")
    print(separator)
    print("OIDC provider ARN:")
    print(f"  {provider_arn}")
    print(separator)


if __name__ == "__main__":
    main()
