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


# Entrada de los datos a procesar
module "input_data" {
  source      = "../modules/s3-bucket"
  bucket_name = "data-input"
}
