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
    bucket         = "dev-aws-lifecycle-automation-terraform-state"
    key            = "dev/terraform.tfstate"
    encrypt        = true
    dynamodb_table = "dev-ws-lifecycle-automation-terraform-locks"
  }
}
