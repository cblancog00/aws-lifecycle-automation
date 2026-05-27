#!/bin/bash
# Despliega o actualiza los stacks de CloudFormation que crean los roles IAM
# de GitHub Actions (plan y apply) para este proyecto.
#
# Uso:
#   ./pipeline-roles-bootstrap.sh [plan|apply] [dev|prod]
#
# Ejemplos:
#   ./pipeline-roles-bootstrap.sh plan dev
#   ./pipeline-roles-bootstrap.sh apply prod

set -euo pipefail

# --- Configuracion general ---
AWS_REGION="eu-central-1"
GITHUB_ORG="cblancog00"
GITHUB_REPO="aws-lifecycle-automation"

# --- Rutas a las plantillas de CloudFormation ---
CFN_PLAN_TEMPLATE_PATH="./pipeline-plan-role-bootstrap.yml"
CFN_APPLY_TEMPLATE_PATH="./pipeline-apply-role-bootstrap.yml"

# --- Function para desplegar o actualizar un stack de CloudFormation ---
deploy_stack() {
    local STACK_NAME=$1
    local TEMPLATE_PATH=$2
    local ROLE_NAME=$3
    local TF_STATE_BUCKET=$4
    local TF_LOCK_TABLE=$5

    echo "--- Deploying/Updating Stack: $STACK_NAME ---"

    aws cloudformation deploy \
        --template-file "$TEMPLATE_PATH" \
        --stack-name "$STACK_NAME" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION" \
        --parameter-overrides \
            RoleName="$ROLE_NAME" \
            GitHubOrg="$GITHUB_ORG" \
            GitHubRepo="$GITHUB_REPO" \
            TerraformStateBucket="$TF_STATE_BUCKET" \
            TerraformLockTable="$TF_LOCK_TABLE"

    if [ $? -eq 0 ]; then
        echo "Stack '$STACK_NAME' deployed/updated successfully."
        aws cloudformation describe-stacks \
            --stack-name "$STACK_NAME" \
            --query "Stacks[0].Outputs" \
            --region "$AWS_REGION" \
            --output table
    else
        echo "Error deploying/updating stack '$STACK_NAME'."
        exit 1
    fi
}

# --- Validacion de argumentos ---
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [plan|apply] [dev|prod]"
    echo "Example: $0 plan dev"
    echo "         $0 apply prod"
    exit 1
fi

ROLE_TYPE=$1
ENVIRONMENT=$2

# Validar entorno
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Invalid environment '$ENVIRONMENT'. Must be 'dev' or 'prod'."
    exit 1
fi

# Nombres de los recursos del backend de Terraform para cada entorno.
# El bucket sigue el patron del bootstrap: tfstate-{account_id}-{env}
# La tabla sigue el patron: tfstate-lock-{env}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TF_STATE_BUCKET="tfstate-${AWS_ACCOUNT_ID}-${ENVIRONMENT}"
TF_LOCK_TABLE="tfstate-lock-${ENVIRONMENT}"

case "$ROLE_TYPE" in
    "plan")
        STACK_NAME="github-actions-terraform-plan-role-${ENVIRONMENT}"
        ROLE_NAME="github-actions-terraform-plan-${ENVIRONMENT}"

        echo "Preparing to deploy PLAN role for environment: $ENVIRONMENT"
        deploy_stack "$STACK_NAME" "$CFN_PLAN_TEMPLATE_PATH" "$ROLE_NAME" "$TF_STATE_BUCKET" "$TF_LOCK_TABLE"
        ;;
    "apply")
        STACK_NAME="github-actions-terraform-apply-role-${ENVIRONMENT}"
        ROLE_NAME="github-actions-terraform-apply-${ENVIRONMENT}"

        echo "Preparing to deploy APPLY role for environment: $ENVIRONMENT"
        deploy_stack "$STACK_NAME" "$CFN_APPLY_TEMPLATE_PATH" "$ROLE_NAME" "$TF_STATE_BUCKET" "$TF_LOCK_TABLE"
        ;;
    *)
        echo "Invalid role type '$ROLE_TYPE'. Must be 'plan' or 'apply'."
        echo "Usage: $0 [plan|apply] [dev|prod]"
        exit 1
        ;;
esac
