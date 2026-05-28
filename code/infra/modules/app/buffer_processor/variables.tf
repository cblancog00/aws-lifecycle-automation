variable "environment" {
  description = "Entorno de despliegue (p. ej., dev, prod)"
  type        = string
}

variable "processor_queue_arn" {
  description = "ARN de la cola SQS principal que dispara la Lambda"
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
