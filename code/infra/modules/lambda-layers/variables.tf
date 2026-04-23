variable "build_script_path" {
  type        = string
  description = "Script path"
  default     = null
  nullable    = true
}

variable "layer_requirements_lockfile" {
  type        = string
  description = "Lock file name uv.lock, poetry.lock, etc..."
  default     = "uv.lock"
}

variable "layer_requirements_path" {
  type        = string
  description = "Directory of pyproject.toml"
}

variable "layer_name" {
  type        = string
  description = "Name of the Lambda Layer"
}

variable "layer_bucket_id" {
  type        = string
  description = "Bucket where the layer will be stored"
}

variable "python_version" {
  type        = string
  description = "Python version to use for Lambda Layer"
  default     = "3.12"
  validation {
    condition     = can(regex("^3\\.(8|9|10|11|12|13|14)$", var.python_version))
    error_message = "Python version should be 3.X"
  }
}

variable "architecture" {
  type        = string
  description = "The architecture of the lambda runtime"
  default     = "arm64"
}
