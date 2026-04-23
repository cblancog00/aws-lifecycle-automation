variable "environment" {
  description = "Entorno de despliegue (p. ej., dev, prod)"
  type        = string
}

variable "dynamodb_stream_arn" {
  description = "ARN del stream de DynamoDB del que leer los eventos"
  type        = string
}
