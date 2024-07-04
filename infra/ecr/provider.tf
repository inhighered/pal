# config.tf
provider "aws" {
  region  = "us-east-2"
#  profile = "tfuser"
}

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.69.0"
    }
  }
}