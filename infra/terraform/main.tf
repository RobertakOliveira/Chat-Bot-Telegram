# VPC
module "vpc" {
  source = "./modules/vpc"
  
  cidr_block = "10.0.0.0/16"
  vpc_name   = "${var.project}-vpc"
}

# S3
module "s3" {
  source             = "./modules/s3"
  bucket_name_prefix = "grupo1-chatbot-documentos"
  bucket_tag_name    = "grupo1ChatbotDocuments"
  project            = var.project
  cost_center        = var.cost_center

  dataset_path       = "${path.root}/../../dataset/juridicos.zip"
}

# EC2
module "ec2" {
  source            = "./modules/ec2"
  ami               = "ami-07a6f770277670015"
  instance_type     = "t2.micro"
  subnet_id         = module.vpc.public_subnet_id
  security_group_id = module.vpc.security_group_id
}

# CloudWatch
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  log_group_name   = "/aws/chatbot/legal-documents"
  retention_in_days = 7
}

# API Gateway
module "api_gateway" {
  source          = "./modules/api_gateway"
  api_name        = "Grupo1ChatbotAPI"
  api_description = "API para o Chatbot"
  resource_path   = "proxy"
  stage_name      = "prod"
}

# IAM Role e Policy
module "iam" {
  source      = "./modules/iam"
  role_name   = "Grupo1ChatbotRole"
  service     = "ec2.amazonaws.com"
  policy_name = "Grupo1ChatbotPolicy"
}
