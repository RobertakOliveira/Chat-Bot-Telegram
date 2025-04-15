variable "log_group_name" {
  description = "Nome do Log Group no CloudWatch"
  type        = string
}

variable "retention_in_days" {
  description = "Dias de retenção dos logs"
  type        = number
  default     = 7
}

variable "project" {
  description = "Nome do projeto"
  type        = string
  default     = "Grupo1Chatbot"
}
