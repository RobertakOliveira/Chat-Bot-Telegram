variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "owner_tag" {
  description = "Identificador do responsável"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}

variable "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  type        = string
}