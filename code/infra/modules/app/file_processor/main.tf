# Función Lambda que procesa los archivos depositados en el bucket de entrada
module "lambda_file_processor" {
  source = "../../common/lambda-functions"

  description   = "Función Lambda para procesar los archivos depositados en el bucket de entrada"
  function_name = local.lambda_name

  handler                        = "main.lambda_handler"
  runtime                        = "python3.12"
  timeout                        = 300
  reserved_concurrent_executions = 1
  memory_size                    = 128

  filename         = data.archive_file.file_processor.output_path
  source_code_hash = data.archive_file.file_processor.output_base64sha256

  aws_lambda_code_signing_config_arn = var.signing_arn

  layers = var.layer_arn != null ? [var.layer_arn] : []

  custom_policies = {
    "${local.lambda_name}-read-s3-policy"      = data.aws_iam_policy_document.lambda_read_s3_policy.json
    "${local.lambda_name}-write-dynamo-policy" = data.aws_iam_policy_document.lambda_write_dynamo_policy.json
  }
  aws_managed_policies = [
    data.aws_iam_policy.AWSLambdaDynamoDBExecutionRole.arn,
  ]

  environment_vars = {
    ENVIRONMENT        = var.environment
    TEMP_DB_TABLE_NAME = var.temp_db_table_name
  }
}

# Permiso para que S3 invoque la función Lambda
resource "aws_lambda_permission" "allow_bucket_execution" {
  statement_id   = "FileProcessorS3Event"
  action         = "lambda:InvokeFunction"
  function_name  = module.lambda_file_processor.lambda_name
  principal      = "s3.amazonaws.com"
  source_arn     = var.input_bucket_arn
  source_account = data.aws_caller_identity.current.account_id
}

# Notificación del bucket S3 para disparar la Lambda al crear objetos
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.input_bucket_name

  lambda_function {
    lambda_function_arn = module.lambda_file_processor.lambda_arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket_execution]
}
