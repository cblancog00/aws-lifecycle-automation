variable "environment" {
  description = "Deployment environment (e.g. dev, prod)"
  type        = string
}

variable "file_processor_layer_path" {
  description = "Path to the file_processor Python project directory, relative to the Terraform working directory"
  type        = string
  default     = "../../../python/file_processor"
}

variable "buffer_processor_layer_path" {
  description = "Path to the buffer_processor Python project directory, relative to the Terraform working directory"
  type        = string
  default     = "../../../python/buffer_processor"
}
