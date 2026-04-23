variable "build_script_path" {
  type        = string
  description = "Ruta al script"
  default     = null
  nullable    = true
}

variable "layer_requirements_lockfile" {
  type        = string
  description = "Nombre del archivo de bloqueo de dependencias uv.lock, poetry.lock, etc..."
  default     = "uv.lock"
}

variable "layer_requirements_path" {
  type        = string
  description = "Directorio del archivo pyproject.toml"
}

variable "layer_name" {
  type        = string
  description = "Nombre del Lambda Layer"
}

variable "layer_bucket_id" {
  type        = string
  description = "Bucket donde se almacenará el layer"
}

variable "python_version" {
  type        = string
  description = "Versión de Python para el Lambda Layer"
  default     = "3.12"
  validation {
    condition     = can(regex("^3\\.(8|9|10|11|12|13|14)$", var.python_version))
    error_message = "La versión de Python debe set 3.X"
  }
}

variable "architecture" {
  type        = string
  description = "Arquitectura del runtime de Lambda"
  default     = "arm64"
}
