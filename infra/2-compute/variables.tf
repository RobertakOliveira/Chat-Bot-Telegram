variable "aws_region" {
  description = "Região AWS"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "instance_type" {
  description = "Tipo de instância EC2"
  type        = string
  default = "t2.micro"
}

variable "vpc_id" {
  description = "ID da VPC"
  type        = string
}

variable "subnet_id" {
  description = "ID da Subnet"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}

variable "owner_tag" {
  description = "Identificador do responsável"
  type        = string
}

variable "s3_bucket_name" {
  description = "Nome do bucket S3 para documentos"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN do bucket S3 para documentos"
  type        = string
}

variable "telegram_bot_token" {
  type        = string
  description = "Token do Bot do Telegram (obtido com @juridico_compasso_grupo_6_bot)"  #
  sensitive   = true # Opcional: evita que o valor seja exibido em logs
}

variable "api_secret_key"{ 
  type        = string
  description = "Chave secreta da API"
  sensitive   = true # Opcional: evita que o valor seja exibido em logs
}