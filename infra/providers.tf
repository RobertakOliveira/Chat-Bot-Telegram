provider "aws" {
  region  = var.aws_region
  profile = "KATCILANE-SOUZA" # Use o perfil que você configurou na AWS CLI
  
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
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    use_lockfile   = true  # Substitui o parâmetro obsoleto
  }
}