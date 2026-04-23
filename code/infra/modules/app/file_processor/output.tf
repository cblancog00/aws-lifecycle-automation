output "lambda_function_name" {
  description = "Nombre de la función Lambda procesadora de archivos"
  value       = module.lambda_file_processor.function_name
}

output "lambda_arn" {
  description = "ARN de la función Lambda procesadora de archivos"
  value       = module.lambda_file_processor.lambda_arn
}
