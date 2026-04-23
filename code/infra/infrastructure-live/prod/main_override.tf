terraform {
  required_version = ">= 1.2.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "<5.93"
    }
  }

  backend "s3" {
    region         = "eu-south-2"
    bucket         = "prod-aws-lifecycle-automation-terraform-state"
    key            = "prod/terraform.tfstate"
    encrypt        = true
    dynamodb_table = "prod-ws-lifecycle-automation-terraform-locks"
  }
}
