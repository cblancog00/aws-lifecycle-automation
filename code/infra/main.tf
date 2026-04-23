#### START | Este bloque de codigo se sobreescribe desde cada entorno ####
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }

  }
  backend "s3" {
  }

}
#### END ###


# Bucket S3 de entrada de los datos a procesar
module "input_data" {
  source      = "../modules/s3-bucket"
  env         = var.environment
  bucket_name = "data-input"
}

# Módulo de procesamiento de archivos
module "file_processor" {
  source = "../modules/app/file_processor"

  environment       = var.environment
  input_bucket_name = module.input_data.bucket_name
  input_bucket_arn  = module.input_data.bucket_arn
}
