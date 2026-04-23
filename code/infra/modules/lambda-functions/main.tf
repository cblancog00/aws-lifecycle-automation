resource "aws_lambda_function" "lambda-function" {
  #checkov:skip=CKV_AWS_117: "Ensure that AWS Lambda function is configured inside a VPC" #TODO
  #checkov:skip=CKV_AWS_116: "Ensure that AWS Lambda function is configured for a Dead Letter Queue(DLQ)"
  #checkov:skip=CKV_AWS_173: "Check encryption settings for Lambda environmental variable"
  #checkov:skip=CKV_AWS_115: "Ensure that AWS Lambda function is configured for function-level concurrent execution limit"
  filename         = var.filename
  source_code_hash = var.source_code_hash

  function_name                  = var.function_name
  role                           = aws_iam_role.lambda_role.arn
  handler                        = var.handler
  runtime                        = var.runtime
  timeout                        = var.timeout
  layers                         = var.layers
  description                    = var.description
  reserved_concurrent_executions = var.reserved_concurrent_executions
  memory_size                    = var.memory_size
  tracing_config {
    mode = var.tracing_mode
  }

  architectures = var.architectures

  environment {
    variables = var.environment_vars
  }

  code_signing_config_arn = var.aws_lambda_code_signing_config_arn

  # To avoid issues with log_group deletions
  depends_on = [aws_cloudwatch_log_group.default, aws_iam_role.lambda_role]
}

resource "aws_cloudwatch_log_group" "default" {
  #checkov:skip=CKV_AWS_158: "Ensure that CloudWatch Log Group is encrypted by KMS"
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 365
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.function_name}_role"
  assume_role_policy = data.aws_iam_policy_document.assume_lambda_role.json
}

resource "aws_iam_policy" "lambda_logs_policy" {
  name   = "${var.function_name}-logging-restricted"
  policy = data.aws_iam_policy_document.log_restricted_policy.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
}

resource "aws_iam_policy" "custom_policies" {
  for_each = var.custom_policies

  name   = each.key
  policy = each.value
}

resource "aws_iam_role_policy_attachment" "custom_policy_attachments" {
  for_each   = aws_iam_policy.custom_policies
  role       = aws_iam_role.lambda_role.name
  policy_arn = each.value.arn
}

resource "aws_iam_role_policy_attachment" "managed_policies" {
  for_each   = toset(var.aws_managed_policies)
  role       = aws_iam_role.lambda_role.name
  policy_arn = each.value
}
