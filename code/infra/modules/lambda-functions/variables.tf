variable "filename" {
  description = "Path to the function's deployment package within the local filesystem"
  type        = string
}

variable "source_code_hash" {
  description = "Used to trigger updates. Must be set to a base64-encoded SHA256 hash of the package file specified with either filename or s3_key"
  type        = string
}

variable "function_name" {
  description = "Unique name for your Lambda Function."
  type        = string
}

variable "handler" {
  description = "Function entrypoint in your code."
  type        = string
}

variable "runtime" {
  description = "Identifier of the function's runtime. See Runtimes for valid values."
  type        = string
}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds."
  type        = string
  default     = 90
}

variable "layers" {
  description = "List of Lambda Layer Version ARNs (maximum of 5) to attach to your Lambda Function."
  type        = list(string)
}

variable "description" {
  description = "Description of what your Lambda Function does."
  type        = string
  default     = null
}

variable "environment_vars" {
  description = "(Required) Whether to sample and trace a subset of incoming requests with AWS X-Ray."
  type        = map(any)
}

variable "reserved_concurrent_executions" {
  description = "reserved_concurrent_executions"
  default     = -1
}

variable "memory_size" {
  description = "Memory size of the lambda"
  default     = 128
}

variable "custom_policies" {
  type        = map(string)
  description = "Map of custom IAM policy names to policy JSON definitions"
  default     = {}
}

variable "aws_managed_policies" {
  description = "List of AWS Managed Policies ARN that needs to be attached to the role"
  type        = list(string)
  default     = []
}

variable "invocation_services" {
  description = "The list of services that will make the invocation of the lambda"
  type        = list(string)
  default     = ["lambda.amazonaws.com"]
}

variable "aws_lambda_code_signing_config_arn" {
  description = "AWS lambda code signing config"
  type        = string
  default     = null
}

variable "architectures" {
  description = "Lambda instruction set architecture"
  type        = list(string)
  default     = ["arm64"] # Use Graviton2 Processor
}

variable "tracing_mode" {
  description = "X-Ray tracing mode for the Lambda function"
  type        = string
  default     = "Active"
}
