# Variáveis para o módulo storage

# Variável: ARN da IAM Role do Chatbot
variable "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  type        = string
}

# Variável: Identificador do responsável pelos recursos
variable "owner_tag" {
  description = "Identificador do responsável pelos recursos (máx. 20 caracteres)"
  type        = string
  validation {
    condition     = length(var.owner_tag) <= 20
    error_message = "O owner_tag deve ter no máximo 20 caracteres."
  }
}

# Variável: Ambiente de implantação
variable "environment" {
  description = "Ambiente de implantação (valores recomendados: dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], lower(var.environment))
    error_message = "Ambiente deve ser 'dev', 'staging' ou 'prod'."
  }
}

# Variável: Prefixo para nomes de buckets
variable "bucket_name_prefix" {
  description = "Prefixo para nomes de buckets (será combinado com owner_tag e random suffix)"
  type        = string
  default     = "chatbot-docs"
}

# Variáveis para habilitar o logging de acesso e configurar o bucket de logs
variable "enable_access_logging" {
  description = "Flag para habilitar o logging de acesso no S3"
  type        = bool
  default     = false  # Defina o valor padrão, se desejar
}

variable "logging_bucket" {
  description = "Nome do bucket S3 onde os logs de acesso serão armazenados"
  type        = string
  default     = ""  # Defina o valor padrão, se desejar
}


# Variável: Tags comuns para todos os recursos
variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
  default     = {}
}

# Variável: Caminho local para os PDFs
variable "dataset_path" {
  type        = string
  description = "Caminho local para os PDFs que serão enviados para o S3"
}
