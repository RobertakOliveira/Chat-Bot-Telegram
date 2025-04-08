
# Configurações Globais
variable "aws_region" {
  description = "Região AWS onde os recursos serão provisionados"
  type        = string
  default     = "us-east-1"
  validation {
    condition     = contains(["us-east-1", "sa-east-1"], var.aws_region)
    error_message = "Use: us-east-1 ou sa-east-1."
  }
}

variable "environment" {
  description = "Ambiente de deploy (dev/staging/prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Valor deve ser: dev, staging ou prod."
  }
}

# Configurações EC2
variable "ami_id" {
  description = "ID da AMI para a instância EC2 (Ubuntu 22.04 LTS recomendado)"
  type        = string
  default     = "ami-123456" # Substitua pelo ID correto para sua região
}

variable "instance_type" {
  description = "Tipo de instância EC2"
  type        = string
  default     = "t3.medium"
  validation {
    condition     = can(regex("^[t][23][a-z]*\\.", var.instance_type))
    error_message = "Use tipos t3 ou t2 com tamanho adequado."
  }
}

# Identificação
variable "owner_tag" {
  description = "Identificador do responsável (apenas letras minúsculas e hífens)"
  type        = string
  default     = "default-user"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.owner_tag))
    error_message = "Use apenas letras minúsculas, números e hífens."
  }
}

# Tags Padronizadas
variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
  default     = {
    Project     = "chatbot-juridico"
    ManagedBy   = "terraform"
    Environment = "dev"
    Repository  = "https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro"
  }
}

# Configurações de Rede
variable "vpc_cidr" {
  description = "Bloco CIDR para a VPC principal"
  type        = string
  default     = "10.0.0.0/16"
  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "Use notação CIDR válida (ex: 10.0.0.0/16)."
  }
}