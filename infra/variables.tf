# Declaração da variável "aws_region", que define a região da AWS onde os recursos serão criados.
# Por padrão, a região é "us-east-1". Há uma validação para garantir que o valor seja "us-east-1" ou "sa-east-1".
variable "aws_region" {
  description = "The AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
  validation {
    condition     = contains(["us-east-1", "sa-east-1"], var.aws_region)
    error_message = "Use: us-east-1 ou sa-east-1."
  }
}

# Declaração da variável "environment", que define o ambiente de deploy (dev, staging ou prod).
# O valor padrão é "dev". Há uma validação para garantir que o valor seja um dos três ambientes permitidos.
variable "environment" {
  description = "Ambiente de deploy (dev/staging/prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Valor deve ser: dev, staging ou prod."
  }
}

# Declaração da variável "owner_tag", que identifica o responsável pelo recurso.
# O valor deve conter apenas letras minúsculas, números e hífens. O padrão é "katcilane".
variable "owner_tag" {
  description = "Identificador do responsável (apenas letras minúsculas e hífens)"
  type        = string
  default     = "katcilane"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.owner_tag))
    error_message = "Use apenas letras minúsculas, números e hífens."
  }
}

# Declaração da variável "instance_type", que define o tipo da instância EC2.
# O valor padrão é "t3.medium". Há uma validação para garantir que o tipo seja um dos permitidos.
variable "instance_type" {
  description = "Tipo da instância EC2"
  type        = string
  default     = "t2.micro"  # Mude para t2.micro
}

# Declaração da variável "common_tags", que define um conjunto de tags comuns para todos os recursos.
# As tags incluem informações como projeto, centro de custo, responsável, ambiente e repositório.
variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
  default = {
    Project     = "chatbot-juridico"
    CostCenter  = "TI"
    ManagedBy   = "terraform"
    Environment = "dev"
    Owner       = "katcilane"  #alterar para o seu nome
    Repository  = "https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro"
  }
}
# Declaração da variável "chatbot_role_arn", que define o ARN da IAM Role do Chatbot.
variable "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  type        = string
  default = ""
}

# ID da instância EC2 que será monitorada
 variable "instance_id" {
   description = "ID da instância EC2 (para métricas e alarms)"
   type        = string
 }