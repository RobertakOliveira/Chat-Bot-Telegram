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

variable "sns_topic_arn" {
  description = "ARN do tópico SNS para notificações de alarmes"
  type        = string
  default     = ""
}

variable "instance_id" {
  description = "ID da instância EC2 para monitoramento"
  type        = string
}
