terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }

  }
}

# Bucket S3 dedicado al almacenamiento de los zips de los Lambda Layers
module "lambda_layer_bucket" {
  source      = "../../common/s3-bucket"
  env         = var.environment
  bucket_name = "lambda-layers"
}

# Layer de dependencias para file_processor (pydantic, boto3)
module "file_processor_layer" {
  source = "../../common/lambda-layers"

  layer_name              = "${var.environment}-file-processor"
  layer_requirements_path = var.file_processor_layer_path
  layer_bucket_id         = module.lambda_layer_bucket.bucket_id
  python_version          = "3.12"
  architecture            = "arm64"
}

# Layer de dependencias para buffer_processor (pydantic, boto3)
module "buffer_processor_layer" {
  source = "../../common/lambda-layers"

  layer_name              = "${var.environment}-buffer-processor"
  layer_requirements_path = var.buffer_processor_layer_path
  layer_bucket_id         = module.lambda_layer_bucket.bucket_id
  python_version          = "3.12"
  architecture            = "arm64"
}
