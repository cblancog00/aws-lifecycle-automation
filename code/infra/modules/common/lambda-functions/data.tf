data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "assume_lambda_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = var.invocation_services
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "log_restricted_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
      "logs:CreateLogStream"
    ]
    resources = ["${aws_cloudwatch_log_group.default.arn}:*"]
  }
}
