provider "aws" {
    region = "us-east-1"
}

module "ecr" {
    source = "./ecr"
}

module "iam" {
  source = "./iam"
}

module "api" {
  source = "./api"

  lambda_telegram_arn  = module.lambda.lambda_telegram_arn
  lambda_telegram_name = module.lambda.lambda_telegram_name
}


module "lambda" {
  source = "./lambda"

  lambda_config = {
    lambda_file   = "lambda_telegram.py"
    handler_name  = "handler"
    tag           = "telegram_rag"
  }

  ecr_repo_url   = module.ecr.repository_url
  exec_role_arn  = module.iam.lambda_exec_role_arn
  aws_region     = var.aws_region
}


