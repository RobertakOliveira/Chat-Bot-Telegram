provider "aws" {
  region = "us-east-1"
  profile = "AdministratorAccess-619071337533"
 
  

  default_tags {
    tags = var.common_tags
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "chatbot-terraform-state-global"
    key            = "chatbot-juridico/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    use_lockfile   = true # Nova abordagem sem DynamoDB
    profile        = "AdministratorAccess-619071337533"
  }
}