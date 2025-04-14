# Módulo de rede (network)
module "network" {
  source       = "./modules/network"
  environment  = var.environment
  vpc_cidr     = "10.0.0.0/16"
  common_tags  = var.common_tags
  aws_region   = var.aws_region
}

# Módulo de armazenamento (storage)
module "storage" {
  source       = "./modules/storage"
  owner_tag    = var.owner_tag
  environment  = var.environment
  common_tags  = var.common_tags
  chatbot_role_arn = module.compute.chatbot_role_arn
  depends_on = [module.network]
}

# Módulo de computação (compute)
module "compute" {
  source        = "./modules/compute"
  environment   = var.environment
  vpc_id        = module.network.vpc_id
  subnet_id     = module.network.public_subnet_id
  instance_type = var.instance_type
  common_tags   = var.common_tags
  owner_tag     = var.owner_tag
  aws_region    = var.aws_region
  
}

module "s3" {
  source       = "./modules/s3"
  dataset_path = "./juridicos"
  project_name = local.project_name
}