variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "project_name" {
  description = "Nome do projeto para filtragem"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}