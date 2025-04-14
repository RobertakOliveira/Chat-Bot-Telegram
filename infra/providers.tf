provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      Owner       = var.owner_tag
      Project     = "chatbot-juridico"
      ManagedBy   = "Terraform"
    }
  }
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

   backend "s3" {
    bucket         = "chatbot-terraform-state-katcilane"
    key            = "chatbot-juridico/${var.environment}/terraform.tfstate" # Melhor organização
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks-${var.owner_tag}" # Integração com o lock
    # Removido use_lockfile (não é um parâmetro válido do backend S3)
  }
}