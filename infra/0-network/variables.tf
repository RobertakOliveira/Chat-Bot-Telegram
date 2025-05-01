variable "vpc_cidr" {
  description = "Bloco CIDR para a VPC"
  type        = string
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

variable "project_name" {
  description = "Nome do projeto"
  type        = string
}