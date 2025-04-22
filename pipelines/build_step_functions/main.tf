provider "aws" {
  region = "us-east-1"
}

module "ecr" {
  source = "./modules/ecr"
}

module "iam" {
  source = "./modules/iam"
}

module "lambda" {
  source             = "./modules/lambda"
  lambda_functions   = var.lambda_functions
  ecr_repo_url       = module.ecr.repository_url
  exec_role_arn      = module.iam.lambda_exec_role_arn
  step_function_arn  = module.step_function.workflow_arn
}

module "apigateway" {
  source            = "./modules/apigateway"
  lambda1_invoke_arn = module.lambda.lambda1_invoke_arn
  lambda1_name        = module.lambda.lambda1_function_name
}

module "step_function" {
  source              = "./modules/step_function"
  role_arn            = module.iam.step_function_role_arn
  lambda_arns         = module.lambda.lambda_arns
}
