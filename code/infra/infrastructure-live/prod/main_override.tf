terraform {
  required_version = ">= 1.2.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "<5.93"
    }
  }

  backend "s3" {
    region         = "eu-central-1"
    bucket         = "tfstate-992382825515-prod"
    key            = "prod/terraform.tfstate"
    encrypt        = true
    dynamodb_table = "tfstate-lock-prod"
  }
}
