output "file_processor_layer_arn" {
  value       = module.file_processor_layer.layer_arn
  description = "ARN del Lambda Layer de file_processor"
}

output "buffer_processor_layer_arn" {
  value       = module.buffer_processor_layer.layer_arn
  description = "ARN del Lambda Layer de buffer_processor"
}

output "lambda_layer_bucket_id" {
  value       = module.lambda_layer_bucket.bucket_id
  description = "ID del bucket S3 donde se almacenan los zips de los layers"
}
