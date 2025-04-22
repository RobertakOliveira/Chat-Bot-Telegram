provider "aws" {
  region = "us-east-1"
}

module "ecr" {
  source = "./modules/ecr"
}

module "iam" {
  source = "./modules/iam"
}

module "lambda_invoke" {
  source            = "./modules/lambda_invoke"
  lambda_config     = var.lambda_functions["lambda1"]
  ecr_repo_url      = module.ecr.repository_url
  exec_role_arn     = module.iam.lambda_exec_role_arn
  step_function_arn = module.step_function.workflow_arn
  aws_region        = var.aws_region 
}


module "lambda" {
  source             = "./modules/lambda"
  lambda_functions   = var.lambda_functions
  ecr_repo_url       = module.ecr.repository_url
  exec_role_arn      = module.iam.lambda_exec_role_arn
  step_function_arn  = module.step_function.workflow_arn
}

module "apigateway" {
  source              = "./modules/apigateway"
  lambda_invoke_arn   = module.lambda_invoke.invoke_arn
  lambda_invoke_name  = module.lambda_invoke.function_name
}

module "step_function" {
  source              = "./modules/step_function"
  role_arn            = module.iam.step_function_role_arn
  lambda_arns         = module.lambda.lambda_arns
}
