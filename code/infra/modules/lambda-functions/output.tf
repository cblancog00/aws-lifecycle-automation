output "lambda_arn" {
  value = aws_lambda_function.lambda-function.arn
}
output "lambda_invoke_arn" {
  value = aws_lambda_function.lambda-function.invoke_arn
}
output "lambda_name" {
  value = aws_lambda_function.lambda-function.function_name
}

output "lambda_assume_role" {
  value = aws_iam_role.lambda_role
}

output "source_code_hash" {
  value = aws_lambda_function.lambda-function.source_code_hash
}

output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.lambda-function.function_name
}
