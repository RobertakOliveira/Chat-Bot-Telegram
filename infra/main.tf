module "network" {
  source       = "./0-network"
  aws_region   = var.aws_region
  environment  = var.environment
  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
  common_tags  = merge(var.common_tags, { Owner = var.owner_tag })
}

module "compute" {
  source          = "./2-compute"
  aws_region      = var.aws_region
  environment     = var.environment
  instance_type   = var.instance_type
  vpc_id          = module.network.vpc_id
  subnet_id       = module.network.public_subnet_id
  common_tags     = var.common_tags
  owner_tag       = var.owner_tag
  s3_bucket_name  = module.storage.docs_bucket_name
  s3_bucket_arn   = module.storage.docs_bucket_arn

}

module "storage" {
  source           = "./1-storage"
  environment      = var.environment
  owner_tag        = var.owner_tag
  common_tags      = var.common_tags
  chatbot_role_arn = module.compute.chatbot_role_arn
}

module "monitoring" {
  source       = "./3-monitoring"
  environment  = var.environment
  aws_region   = var.aws_region
  instance_id  = module.compute.instance_id
  common_tags  = var.common_tags
}
