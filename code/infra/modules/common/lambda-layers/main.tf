resource "null_resource" "lambda_layer" {
  triggers = {
    requirements_hash = local.requirements_hash
    script_hash       = local.script_hash
    requirements_path = var.layer_requirements_path
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = "bash ${local.effective_build_script_path} ${var.layer_requirements_path} ${var.python_version} ${var.architecture} ${local.zip_name}"
  }
}

resource "aws_s3_object" "lambda_layer_zip" {
  bucket      = var.layer_bucket_id
  key         = "lambda_layers/${var.layer_name}/${local.zip_name}"
  source      = abspath("${var.layer_requirements_path}/${local.zip_name}")
  source_hash = abspath("${var.layer_requirements_path}/${local.zip_name}")
  depends_on  = [null_resource.lambda_layer]

  lifecycle {
    replace_triggered_by = [null_resource.lambda_layer]
  }
}

resource "aws_lambda_layer_version" "lambda_layer" {
  s3_bucket                = var.layer_bucket_id
  s3_key                   = aws_s3_object.lambda_layer_zip.key
  layer_name               = var.layer_name
  compatible_runtimes      = ["python${var.python_version}"]
  compatible_architectures = [var.architecture]
  skip_destroy             = true
  source_code_hash         = aws_s3_object.lambda_layer_zip.etag
  depends_on               = [aws_s3_object.lambda_layer_zip]
}
