variable "project_name" {
  description = "Nome do projeto (usado para nomear recursos)"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Ambiente deve ser: dev, staging ou prod"
  }
}