variable "lambda_config" {
  description = "Configuração da Lambda única"
  type = object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  })
}

variable "ecr_repo_url" {
  description = "URL do repositório ECR"
  type        = string
}

variable "exec_role_arn" {
  description = "ARN da IAM Role de execução da Lambda"
  type        = string
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
}

variable "bucket_name" {
  description = "Nome do bucket S3 onde serão armazenados os embeddings"
  type        = string
}

variable "bot_token" {
  description = "Token do Bot do Telegram"
  type        = string
  sensitive   = true
}
