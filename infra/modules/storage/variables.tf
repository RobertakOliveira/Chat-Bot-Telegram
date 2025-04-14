# =============================================
# VARIÁVEIS PRINCIPAIS DE IDENTIFICAÇÃO
# =============================================

variable "owner_tag" {
  description = "Identificador do responsável pelos recursos (máx. 20 caracteres)"
  type        = string
  validation {
    condition     = length(var.owner_tag) <= 20
    error_message = "O owner_tag deve ter no máximo 20 caracteres."
  }
}

variable "environment" {
  description = "Ambiente de implantação (valores recomendados: dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], lower(var.environment))
    error_message = "Ambiente deve ser 'dev', 'staging' ou 'prod'."
  }
}

# =============================================
# VARIÁVEIS DE CONFIGURAÇÃO DO BUCKET S3
# =============================================

variable "bucket_name_prefix" {
  description = "Prefixo para nomes de buckets (será combinado com owner_tag e random suffix)"
  type        = string
  default     = "chatbot-docs"
}

variable "enable_bucket_versioning" {
  description = "Habilita versionamento para os buckets S3"
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "Permite destruir buckets não vazios (usar apenas em ambientes de desenvolvimento)"
  type        = bool
  default     = false
}


# =============================================
# VARIÁVEIS DE LOGGING E MONITORAMENTO
# =============================================

variable "enable_access_logging" {
  description = "Habilita logging de acesso ao bucket S3"
  type        = bool
  default     = false
}

variable "logging_bucket" {
  description = "Nome do bucket para armazenar logs de acesso (obrigatório se enable_access_logging=true)"
  type        = string
  default     = ""
}

# =============================================
# VARIÁVEIS DE CONTROLE DE ACESSO
# =============================================

variable "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot (ex.: arn:aws:iam::123456789012:role/chatbot-role)"
  type        = string
  validation {
    condition     = can(regex("^arn:aws:iam::\\d{12}:role/[a-zA-Z0-9_-]+$", var.chatbot_role_arn))
    error_message = "O ARN da role deve seguir o padrão AWS (arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME)."
  }
}

variable "admin_roles" {
  description = "Lista de ARNs de IAM Roles com acesso administrativo aos buckets"
  type        = list(string)
  default     = []
  validation {
    condition     = alltrue([for arn in var.admin_roles : can(regex("^arn:aws:iam::\\d{12}:role/[a-zA-Z0-9_-]+$", arn))])
    error_message = "Cada ARN deve seguir o padrão AWS (arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME)."
  }
}

# =============================================
# VARIÁVEIS DO DYNAMODB (TERRAFORM STATE LOCK)
# =============================================

variable "create_terraform_state" {
  description = "Controla a criação dos recursos para Terraform State (bucket S3 e DynamoDB)"
  type        = bool
  default     = true
}

variable "dynamodb_table_attributes" {
  description = "Atributos adicionais para a tabela DynamoDB"
  type = list(object({
    name = string
    type = string
  }))
  default = []
}

# =============================================
# VARIÁVEIS DE TAGS E METADADOS
# =============================================

variable "common_tags" {
  description = "Tags comuns para todos os recursos (padrão: Environment, Owner, Project, ManagedBy)"
  type        = map(string)
  default     = {}
}

variable "additional_tags" {
  description = "Tags adicionais para todos os recursos"
  type        = map(string)
  default     = {}
}

variable "sensitivity_level" {
  description = "Nível de sensibilidade dos dados (confidential, restricted, internal, public)"
  type        = string
  default     = "confidential"
  validation {
    condition     = contains(["confidential", "restricted", "internal", "public"], var.sensitivity_level)
    error_message = "Valor deve ser: confidential, restricted, internal ou public."
  }
}