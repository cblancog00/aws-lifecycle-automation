output "temp_db_table_name" {
  description = "Nombre de la tabla DynamoDB temporal"
  value       = aws_dynamodb_table.temp_db.name
}

output "temp_db_table_arn" {
  description = "ARN de la tabla DynamoDB temporal"
  value       = aws_dynamodb_table.temp_db.arn
}

output "temp_db_stream_arn" {
  description = "ARN del stream de la tabla DynamoDB temporal"
  value       = aws_dynamodb_table.temp_db.stream_arn
}
