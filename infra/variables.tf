# Declaração de variáveis para o módulo de infraestrutura (sem variáveis de credenciais)

# Configurações globais da infraestrutura
variable "aws_region" {
  description = "Região AWS onde os recursos serão provisionados"
  type        = string
  default     = "us-east-1"
  validation {
    condition     = contains(["us-east-1", "sa-east-1"], var.aws_region)
    error_message = "Região AWS não suportada. Use: us-east-1 ou sa-east-1."
  }
}

variable "owner_tag" {
  description = "Identificador do responsável pelos recursos (use apenas letras minúsculas e hífens)"
  type        = string
  default     = "default-user"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.owner_tag))
    error_message = "Use apenas letras minúsculas, números e hífens."
  }
}

# Configurações de rede (exemplo adicional)
variable "vpc_cidr" {
  description = "Bloco CIDR para a VPC principal"
  type        = string
  default     = "10.0.0.0/16"
}

# Tags padrão para todos os recursos
variable "common_tags" {
  description = "Tags comuns a serem aplicadas em todos os recursos"
  type        = map(string)
  default     = {
    Project     = "chatbot-juridico"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}