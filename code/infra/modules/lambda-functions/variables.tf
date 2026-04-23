variable "filename" {
  description = "Ruta al paquete de despliegue de la función dentro del sistema de archivos local"
  type        = string
}

variable "source_code_hash" {
  description = "Usado para disparar actualizaciones. Debe establecerse con un hash SHA256 codificado en base64 del archivo de paquete especificado con filename o s3_key"
  type        = string
}

variable "function_name" {
  description = "Nombre único para la función Lambda."
  type        = string
}

variable "handler" {
  description = "Punto de entrada de la función en el código."
  type        = string
}

variable "runtime" {
  description = "Identificador del runtime de la función. Consultar Runtimes para valores válidos."
  type        = string
}

variable "timeout" {
  description = "Tiempo máximo de ejecución de la función Lambda en segundos."
  type        = string
  default     = 90
}

variable "layers" {
  description = "Lista de ARNs de versiones de Lambda Layer (máximo 5) para adjuntar a la función Lambda."
  type        = list(string)
}

variable "description" {
  description = "Descripción de lo que have la función Lambda."
  type        = string
  default     = null
}

variable "environment_vars" {
  description = "(Requerido) Variables de entorno para la función Lambda."
  type        = map(any)
}

variable "reserved_concurrent_executions" {
  description = "Número de ejecuciones simultáneas reservadas"
  default     = -1
}

variable "memory_size" {
  description = "Tamaño de memoria de la función Lambda"
  default     = 128
}

variable "custom_policies" {
  type        = map(string)
  description = "Mapa de nombres de políticas IAM personalizadas a sus definiciones JSON"
  default     = {}
}

variable "aws_managed_policies" {
  description = "Lista de ARNs de políticas gestionadas de AWS que deben adjuntarse al rol"
  type        = list(string)
  default     = []
}

variable "invocation_services" {
  description = "Lista de servicios que invocarán la función Lambda"
  type        = list(string)
  default     = ["lambda.amazonaws.com"]
}

variable "aws_lambda_code_signing_config_arn" {
  description = "Configuración de firma de código de AWS Lambda"
  type        = string
  default     = null
}

variable "architectures" {
  description = "Arquitectura del conjunto de instrucciones de Lambda"
  type        = list(string)
  default     = ["arm64"] # Usar procesador Graviton2
}

variable "tracing_mode" {
  description = "Modo de rastreo X-Ray para la función Lambda"
  type        = string
  default     = "Active"
}
