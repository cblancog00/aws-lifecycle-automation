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
# Load leveling buffer: receives temp_db inserts via EventBridge Pipe and queues them for processing
module "load_leveling_buffer" {
  source = "../../modules/app/load_leveling_buffer"

  environment         = var.environment
  dynamodb_stream_arn = module.dynamo_tables.temp_db_stream_arn
}
# Lambda Layers: pydantic + paquete fuente 'common'
module "lambda_layers" {
  source      = "../../modules/app/lambda-layers"
  environment = var.environment
}

# Módulo de procesamiento de archivos
module "file_processor" {
  source = "../../modules/app/file_processor"

  environment        = var.environment
  input_bucket_name  = module.input_data.bucket_name
  input_bucket_arn   = module.input_data.bucket_arn
  temp_db_table_name = module.dynamo_tables.temp_db_table_name
  layer_arn          = module.lambda_layers.file_processor_layer_arn
}

# Módulo de procesamiento de la cola SQS
module "buffer_processor" {
  source = "../../modules/app/buffer_processor"

  environment         = var.environment
  processor_queue_arn = module.load_leveling_buffer.processor_queue_arn
  layer_arn           = module.lambda_layers.buffer_processor_layer_arn
}
