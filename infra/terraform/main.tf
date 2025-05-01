# Configuração do provedor AWS
provider "aws" {
  region = "us-east-1"
}

# Módulo VPC
module "vpc" {
  source     = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
  vpc_name   = "chatbot-vpc"
}

# Módulo S3
module "s3" {
  source             = "./modules/s3"
  bucket_name_prefix = "chatbot-documentos"
  bucket_tag_name    = "chatbotDocuments"
  project            = "chatbot"
  cost_center        = "TI"
  dataset_folder_path = "${path.root}/../../dataset/juridicos"
}

# Módulo IAM
module "iam" {
  source      = "./modules/iam"
  role_name   = "ChatbotRole"
  policy_name = "ChatbotPolicy"
  service     = "ec2.amazonaws.com"
}

# Módulo EC2
module "ec2" {
  source              = "./modules/ec2"
  ami                 = "ami-0b5eea76982371e91"
  instance_type       = "t2.micro"
  subnet_id           = module.vpc.public_subnet_id
  security_group_id   = module.vpc.security_group_id
  log_group_name      = "chatbot-logs"
  iam_instance_profile_name = module.iam.instance_profile_name
}

# Módulo CloudWatch
module "cloudwatch" {
  source = "./modules/cloudwatch"
  log_group_name = "chatbot-logs"
  instance_id = module.ec2.instance_id
}

# Módulo API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"
  api_name = "ChatbotAPI"
  api_description = "API para o Chatbot"
  resource_path = "proxy"
  stage_name = "prod"
}
