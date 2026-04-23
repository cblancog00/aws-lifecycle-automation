variable "environment" {
  description = "Entorno de despliegue (p. ej., dev, prod)"
  type        = string
}

variable "input_bucket_name" {
  description = "Nombre del bucket S3 de entrada de datos"
  type        = string
}

variable "input_bucket_arn" {
  description = "ARN del bucket S3 de entrada de datos"
  type        = string
}

variable "layer_arn" {
  description = "ARN del Lambda Layer a adjuntar (opcional)"
  type        = string
  default     = null
  nullable    = true
}

variable "signing_arn" {
  description = "ARN de la configuración de firma de código para Lambda (opcional)"
  type        = string
  default     = null
  nullable    = true
}

variable "temp_db_table_name" {
  description = "Nombre de la tabla DynamoDB temporal donde la Lambda escribirá los registros procesados"
  type        = string
}
