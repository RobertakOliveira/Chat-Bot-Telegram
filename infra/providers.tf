provider "aws" {
  region = var.aws_region
   profile = "AdministratorAccess-619071337533"  #É necessário ter o perfil configurado no seu AWS CLI pois não é possível passar credenciais diretamente no provider do Terraform.
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
    key            = "chatbot-juridico/terraform.tfstate" # Caminho fixo ou mude manualmente por ambiente
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks" # Nome fixo da tabela
    profile        = "AdministratorAccess-619071337533"  # É necessário ter o perfil configurado no seu AWS CLI pois não é possível passar credenciais diretamente no provider do Terraform.
  }
}