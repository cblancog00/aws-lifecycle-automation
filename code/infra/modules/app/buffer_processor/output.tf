output "lambda_arn" {
  description = "ARN de la función Lambda buffer_processor"
  value       = module.lambda_buffer_processor.lambda_arn
}

output "lambda_name" {
  description = "Nombre de la función Lambda buffer_processor"
  value       = module.lambda_buffer_processor.lambda_name
}
