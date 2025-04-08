# Variables para o módulo VPC
# Declaração de variáveis para o módulo VPC (sem variáveis de credenciais)



variable "vpc_cidr" {
  description = "Bloco CIDR para a VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}