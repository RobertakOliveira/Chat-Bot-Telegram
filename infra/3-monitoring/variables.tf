variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
}

variable "instance_id" {
  description = "ID da instância EC2 para monitoramento"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}