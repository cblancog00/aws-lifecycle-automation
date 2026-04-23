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
  source      = "../../modules/common/s3-bucket"
  env         = var.environment
  bucket_name = "data-input"
}

# Tablas DynamoDB de la aplicación
module "dynamo_tables" {
  source      = "../../modules/app/dynamo_tables"
  environment = var.environment
}
# Fan-out buffer: propaga inserciones de temp_db via EventBridge Pipe → SNS → SQS
module "fan_out_buffer" {
  source = "../../modules/app/fan_out_buffer"

  environment         = var.environment
  dynamodb_stream_arn = module.dynamo_tables.temp_db_stream_arn
}
# Módulo de procesamiento de archivos
module "file_processor" {
  source = "../../modules/app/file_processor"

  environment        = var.environment
  input_bucket_name  = module.input_data.bucket_name
  input_bucket_arn   = module.input_data.bucket_arn
  temp_db_table_name = module.dynamo_tables.temp_db_table_name
}
