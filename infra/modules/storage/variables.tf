variable "owner_tag" {
  description = "Identificador do responsável pelos recursos"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}

variable "create_terraform_state" {
  description = "Define se deve criar o bucket de Terraform State"
  type        = bool
  default     = true
}

variable "environment" {
  description = "Ambiente (dev/staging/prod)"
  type        = string
}

variable "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  type        = string
}