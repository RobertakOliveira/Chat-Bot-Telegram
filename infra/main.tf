# Módulo de rede (network)
module "network" {
  source      = "./modules/network"
  environment = var.environment
  vpc_cidr    = "10.0.0.0/16"
  common_tags = var.common_tags
  aws_region  = var.aws_region
}

# Módulo de computação (compute) - Agora cria o chatbot_role
module "compute" {
  source         = "./modules/compute"
  environment    = var.environment
  vpc_id         = module.network.vpc_id
  subnet_id      = module.network.public_subnet_id
  instance_type  = var.instance_type
  common_tags    = var.common_tags
  owner_tag      = var.owner_tag
  aws_region     = var.aws_region
  s3_bucket_name = module.storage.docs_bucket_name
  chroma_bucket_name = module.storage.chroma_db_bucket_name
  
  depends_on = [module.network]
}

# Módulo de armazenamento (storage) - Recebe o ARN do Role do compute
module "storage" {
  source           = "./modules/storage"
  owner_tag        = var.owner_tag
  environment      = var.environment
  common_tags      = var.common_tags
  chatbot_role_arn = module.compute.chatbot_role_arn  # ARN do role agora passado diretamente
  dataset_path     = "./juridicos"

  depends_on       = [module.network]
}

# Recurso null_resource para gerar o ChromaDB após os buckets serem criados
resource "null_resource" "generate_chromadb" {
  depends_on = [module.storage]

  provisioner "local-exec" {
    command = <<-EOT
      python3 ./chat/scripts/ingest.py && 
      aws s3 cp ./chroma_db.tar.gz s3://${module.storage.chroma_bucket_name}/ && 
      aws s3 cp ./ready_flag s3://${module.storage.chroma_bucket_name}/ready_flag
    EOT
    environment = {
      PDF_BUCKET = module.storage.docs_bucket_name
    }
  }
}
