# Bootstrap

El bootstrap crea los tres prerrequisitos que deben existir antes de que Terraform pueda gestionar cualquier infraestructura:

1. **Backend remoto de Terraform** — bucket S3 (estado) y tabla DynamoDB (bloqueo).
2. **Proveedor OIDC de GitHub Actions** — permite que los flujos de trabajo asuman roles IAM sin credenciales estáticas.
3. **Rol IAM para Terraform** — rol asumido por GitHub Actions con permisos de mínimo privilegio.

## Prerrequisitos

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Python | 3.11 | [python.org](https://www.python.org/downloads/) |
| uv | 0.4.0 | `pip install uv` o [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| AWS CLI | 2.x | [docs.aws.amazon.com/cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| Cuenta AWS | — | Con permisos suficientes para crear roles IAM, buckets S3 y tablas DynamoDB |

> **Nota:** el AWS CLI no es invocado directamente por los scripts, pero es la forma más cómoda de configurar las credenciales locales que boto3 leerá automáticamente.

## Configurar credenciales AWS

```bash
aws configure
# O bien exportar variables de entorno:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...   # solo si se usan credenciales temporales
```

Las credenciales deben pertenecer a un usuario o rol con permisos para:
- Crear/eliminar buckets S3 y configurar sus políticas.
- Crear/eliminar tablas DynamoDB.
- Crear proveedores OIDC y roles IAM con políticas inline.

## Instalar dependencias

```bash
cd bootstrap/
uv sync
```

## Ejecutar el bootstrap

```bash
uv run python bootstrap.py \
    --region <región>       \
    --github-org <org>      \
    --github-repo <repo>    \
    --environment dev        # o prod
```

### Parámetros

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `--region` | Sí | Región AWS donde se crean los recursos (p. ej. `eu-west-1`) |
| `--github-org` | Sí | Organización o usuario de GitHub dueño del repositorio |
| `--github-repo` | Sí | Nombre del repositorio (sin el prefijo de organización) |
| `--environment` | No | `dev` (por defecto) o `prod` |

### Salida esperada

Al finalizar, el script imprime:

```
------------------------------------------------------------
Bootstrap completado correctamente.
------------------------------------------------------------
Configuración del backend de Terraform:
  bucket         = "tfstate-<account_id>-dev"
  key            = "dev/terraform.tfstate"
  region         = "eu-west-1"
  dynamodb_table = "tfstate-lock-dev"
  encrypt        = true
------------------------------------------------------------
Secrets / variables para GitHub Actions:
  AWS_REGION   = eu-west-1
  AWS_ROLE_ARN = arn:aws:iam::<account_id>:role/github-actions-terraform-dev
------------------------------------------------------------
```

Añade `AWS_REGION` y `AWS_ROLE_ARN` como secrets en el repositorio de GitHub (**Settings → Secrets and variables → Actions**).

## Idempotencia

El script puede ejecutarse varias veces sin efectos secundarios: comprueba la existencia de cada recurso antes de crearlo y sobreescribe únicamente las políticas IAM para mantenerlas sincronizadas con el código fuente.
