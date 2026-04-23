data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Empaqueta el código Python de la función Lambda
data "archive_file" "file_processor" {
  type        = "zip"
  excludes    = [".venv", "__pycache__"]
  source_dir  = "../../../python/file_processor"
  output_path = "${local.lambda_name}.zip"
}

# Política IAM que permite a la Lambda leer objetos del bucket de entrada
data "aws_iam_policy_document" "lambda_read_s3_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject"
    ]
    resources = [
      var.input_bucket_arn,
      "${var.input_bucket_arn}/*"
    ]
  }
}
