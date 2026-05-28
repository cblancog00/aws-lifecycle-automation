data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Managed policy que concede a Lambda los permisos básicos sobre SQS y CloudWatch Logs
data "aws_iam_policy" "AWSLambdaSQSQueueExecutionRole" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}

# Empaqueta el código Python de la función Lambda
data "archive_file" "buffer_processor" {
  type        = "zip"
  excludes    = [".venv", "__pycache__"]
  source_dir  = "../../../python/buffer_processor"
  output_path = "${local.lambda_name}.zip"
}

# Política IAM con permisos de lectura/borrado sobre la cola SQS específica
data "aws_iam_policy_document" "lambda_read_sqs_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ChangeMessageVisibility"
    ]
    resources = [var.processor_queue_arn]
  }
}
