# Módulo de rede (network)
module "network" {
  source      = "./modules/network"
  environment = var.environment
  vpc_cidr    = "10.0.0.0/16"
  common_tags = var.common_tags
  aws_region  = var.aws_region
}

# Módulo de armazenamento (storage) - PRIMEIRO PASSO
module "storage" {
  source           = "./modules/storage"
  owner_tag        = var.owner_tag
  environment      = var.environment
  common_tags      = var.common_tags
  chatbot_role_arn = module.compute.chatbot_role_arn
  dataset_path     = "./juridicos"
  
  depends_on = [module.network]
}

# Geração do ChromaDB - SEGUNDO PASSO
resource "null_resource" "generate_chromadb" {
  depends_on = [module.storage]  # 🔥 Garante que os buckets existam antes

  provisioner "local-exec" {
    command     = "python ../chat/scripts/ingest.py"
    working_dir = "${path.module}/.."  # Ajusta o diretório de trabalho
    
    environment = {
      PDF_BUCKET      = module.storage.docs_bucket_name
      CHROMA_BUCKET   = module.storage.chroma_db_bucket_name
    }
  }
}

# Módulo de computação (compute) - TERCEIRO PASSO
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
  
  depends_on = [null_resource.generate_chromadb]  # ⚠️ Sobe só após o ChromaDB estar pronto
}

