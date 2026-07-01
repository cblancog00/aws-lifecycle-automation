# AWS Lifecycle Automation

Automatización del ciclo de vida completo de una aplicación web serverless en AWS, desde el bootstrapping del entorno hasta su destrucción controlada.

Este proyecto constituye la implementación práctica del Trabajo Fin de Grado *"Automatización del ciclo de vida de una aplicación web serverless en AWS"* (UNIR, Grado en Ingeniería Informática).

## Descripción

El sistema automatiza de forma integral las cinco fases del ciclo de vida de una aplicación serverless:

1. **Bootstrapping** — Scripts Python/boto3 que crean los prerrequisitos de Terraform (backend remoto S3 + DynamoDB, proveedor OIDC, roles IAM).
2. **Aprovisionamiento** — Infraestructura definida como código con Terraform: arquitectura event-driven con S3, Lambda, DynamoDB Streams, EventBridge Pipes, SNS, SQS y DLQ.
3. **Despliegue y actualización** — Pipelines de GitHub Actions con autenticación OIDC (sin credenciales estáticas), detección de cambios basada en hashes y despliegue selectivo.
4. **Rollback** — Reaplicación del pipeline sobre un commit anterior, aprovechando la convergencia declarativa de Terraform.
5. **Destrucción controlada** — `terraform destroy` con protecciones (`prevent_destroy`) que requieren modificación explícita del código.

La seguridad se integra como barrera transversal mediante Checkov (IaC), Bandit (Python) y pre-commit hooks, tanto en el entorno local como en el pipeline de CI.

## Arquitectura de la aplicación

La aplicación de demostración sigue un patrón event-driven con nivelación de carga (Queue-Based Load Leveling):

```
S3 (fichero) → Lambda (file processor) → DynamoDB (+ Streams)
    → EventBridge Pipes → SNS → SQS (+ DLQ) → Lambda (buffer processor)
```

## Estructura del repositorio

```
├── bootstrap/              # Scripts Python de bootstrapping (boto3)
│   ├── bootstrap.py        # Orquestador principal
│   ├── backend.py          # Creación del backend remoto de Terraform
│   ├── oidc.py             # Registro del proveedor OIDC de GitHub
│   ├── iam.py              # Creación de roles IAM para pipelines
│   ├── config.py           # Configuración centralizada de nombres
│   └── tests/              # Tests unitarios (pytest)
├── code/
│   ├── infra/              # Infraestructura como código (Terraform)
│   │   ├── main.tf         # Composición de módulos
│   │   ├── modules/
│   │   │   ├── common/     # Módulos reutilizables (S3, Lambda, capas)
│   │   │   └── app/        # Módulos de aplicación (DynamoDB, buffer, processors)
│   │   └── infrastructure-live/
│   │       ├── dev/        # Configuración del entorno de desarrollo
│   │       └── prod/       # Configuración del entorno de producción
│   ├── python/             # Código de las funciones Lambda
│   │   ├── common/         # Biblioteca compartida (modelos, DB adapter)
│   │   ├── file_processor/ # Lambda: procesa ficheros de S3
│   │   ├── buffer_processor/ # Lambda: procesa mensajes de SQS
│   │   └── tests/          # Tests unitarios y de integración
│   └── pipeline/           # Plantillas auxiliares de pipeline
├── .github/workflows/
│   ├── ci.yml              # Pipeline de integración continua
│   └── deployment.yml      # Pipeline de despliegue (plan + apply)
├── .pre-commit-config.yaml # Hooks de calidad y seguridad
├── docs/                   # Documentación adicional
│   └── bootstrap.md        # Guía detallada del bootstrapping
└── ruff.toml               # Configuración de Ruff (linter/formatter Python)
```

## Requisitos previos

| Herramienta | Versión mínima | Propósito |
|---|---|---|
| Python | 3.11 | Scripts de bootstrapping y funciones Lambda |
| uv | 0.4.0 | Gestión de dependencias Python |
| Terraform | 1.5+ | Aprovisionamiento de infraestructura |
| AWS CLI | 2.x | Configuración de credenciales locales |
| pre-commit | 3.x | Hooks de calidad y seguridad |
| Cuenta AWS | — | Con permisos para crear IAM, S3, DynamoDB, Lambda, SQS, SNS, EventBridge |

## Despliegue completo

### 1. Bootstrap del entorno

```bash
cd bootstrap/
uv sync
uv run python bootstrap.py \
    --region eu-west-1 \
    --github-org <tu-org> \
    --github-repo <tu-repo> \
    --environment dev
```

Esto crea el backend remoto de Terraform, el proveedor OIDC y los roles IAM. Ver [docs/bootstrap.md](docs/bootstrap.md) para detalles.

### 2. Configurar secretos en GitHub

Añadir como variables del repositorio los valores que imprime el script:
- `AWS_REGION` — Región AWS
- `AWS_ROLE_ARN` — ARN del rol IAM para los pipelines

### 3. Aprovisionamiento de infraestructura

Ejecutar el workflow **Deployment** desde la interfaz de GitHub Actions seleccionando el entorno destino (`dev` o `prod`). El pipeline:
1. Se autentica mediante OIDC (sin credenciales estáticas)
2. Ejecuta `terraform plan` y persiste el plan como artefacto
3. Ejecuta `terraform apply` sobre el plan generado

Para producción, se requiere aprobación manual antes del apply.

### 4. Verificación

Depositar el fichero `code/python/sample_data/sample_users.json` en el bucket S3 de entrada para activar el flujo completo de la aplicación.

### 5. Rollback

Ejecutar el workflow de Deployment apuntando a un commit anterior. Terraform calcula y aplica solo las diferencias necesarias para restaurar el estado previo.

### 6. Destrucción

Ejecutar `terraform destroy` desde el pipeline. Los buckets S3 están protegidos con `prevent_destroy`; para eliminarlos, modificar el código y pasar por el flujo de revisión de PR.

## Pipelines de CI/CD

### Integración continua (`ci.yml`)
Se ejecuta en cada pull request. Tres jobs en paralelo:
- **pre-commit** — Terraform fmt, Checkov, Ruff, detección de secretos
- **tests** — pytest sobre scripts de bootstrapping
- **SAST** — Bandit con umbrales de severidad configurados

### Despliegue (`deployment.yml`)
Se ejecuta manualmente (`workflow_dispatch`). Fases separadas de plan y apply con roles IAM diferenciados y protección de entornos para producción.

## Herramientas de calidad y seguridad

| Herramienta | Alcance | Ejecución |
|---|---|---|
| Checkov | Análisis de seguridad de IaC (Terraform) | pre-commit + CI |
| Bandit | Análisis de seguridad de código Python | pre-commit + CI |
| Ruff | Formateo y linting de Python | pre-commit + CI |
| terraform fmt | Formato de Terraform | pre-commit + CI |
| codespell | Corrección ortográfica | pre-commit |

## Documentación

| Documento | Descripción |
|---|---|
| [docs/bootstrap.md](docs/bootstrap.md) | Prerrequisitos y pasos detallados para ejecutar el bootstrap |

## Licencia

Este proyecto se distribuye bajo la licencia indicada en [LICENSE](LICENSE).
