variable "api_name" {
  description = "Nome do API Gateway REST"
  type        = string
}

variable "api_description" {
  description = "Descrição da API"
  type        = string
  default     = "API Gateway criado via módulo Terraform."
}

variable "resource_path" {
  description = "Path que será criado no API Gateway"
  type        = string
  default     = "proxy"
}

variable "stage_name" {
  description = "Nome do stage para o deployment da API"
  type        = string
  default     = "prod"
}
