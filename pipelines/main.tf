module "s3_dataset" {
  source = "./modules/s3_dataset"
  bucket_name = var.bucket_name
}

module "lambda_bot" {
  source = "./modules/lambda_bot"
  lambda_name = var.lambda_name
  s3_bucket = module.s3_dataset.bucket_name
  telegram_token = var.telegram_token
}

module "api_gateway" {
  source = "./modules/api_gateway"
  lambda_function_arn = module.lambda_bot.lambda_arn
}

module "cloudwatch_logs" {
  source = "./modules/cloudwatch_logs"
  log_group_name = var.log_group_name
}

module "bedrock_config" {
  source = "./modules/bedrock_config"
  lambda_name = var.lambda_name
}