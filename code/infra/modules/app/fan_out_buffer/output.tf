output "sns_topic_arn" {
  description = "ARN del topic SNS que distribuye los eventos de insercion"
  value       = aws_sns_topic.this.arn
}

output "processor_queue_arn" {
  description = "ARN de la cola SQS que recibira los eventos para procesar"
  value       = aws_sqs_queue.processor.arn
}

output "processor_queue_url" {
  description = "URL de la cola SQS que recibira los eventos para procesar"
  value       = aws_sqs_queue.processor.url
}

output "processor_dlq_arn" {
  description = "ARN de la cola de mensajes fallidos (DLQ)"
  value       = aws_sqs_queue.processor_dlq.arn
}

output "processor_dlq_url" {
  description = "URL de la cola de mensajes fallidos (DLQ)"
  value       = aws_sqs_queue.processor_dlq.url
}
