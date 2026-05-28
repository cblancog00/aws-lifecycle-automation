# Función Lambda que consume mensajes de la cola SQS y los reencola en la DLQ en caso de fallo
module "lambda_buffer_processor" {
  source = "../../common/lambda-functions"

  description   = "Procesa mensajes de la cola SQS; los reintentos fallidos se redirigen a la DLQ automáticamente"
  function_name = local.lambda_name

  handler     = "main.lambda_handler"
  runtime     = "python3.12"
  timeout     = 300
  memory_size = 128

  filename         = data.archive_file.buffer_processor.output_path
  source_code_hash = data.archive_file.buffer_processor.output_base64sha256

  aws_lambda_code_signing_config_arn = var.signing_arn

  layers = var.layer_arn != null ? [var.layer_arn] : []

  custom_policies = {
    "${local.lambda_name}-read-sqs-policy" = data.aws_iam_policy_document.lambda_read_sqs_policy.json
  }
  aws_managed_policies = [
    data.aws_iam_policy.AWSLambdaSQSQueueExecutionRole.arn,
  ]

  environment_vars = {
    ENVIRONMENT = var.environment
  }
}

# Event source mapping: SQS dispara la Lambda al recibir mensajes en la cola
# ReportBatchItemFailures permite fallos parciales de lote; los mensajes fallidos
# agotan sus reintentos en SQS y pasan a la DLQ por la redrive_policy de la cola
resource "aws_lambda_event_source_mapping" "processor_queue" {
  event_source_arn        = var.processor_queue_arn
  function_name           = module.lambda_buffer_processor.lambda_arn
  batch_size              = 10
  function_response_types = ["ReportBatchItemFailures"]
}
