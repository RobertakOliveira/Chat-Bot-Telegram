variable "lambda_telegram_arn" {
  description = "ARN de invocação da Lambda Telegram"
  type        = string
}

variable "lambda_telegram_name" {
  description = "Nome da função Lambda Telegram para liberar permissão via API Gateway"
  type        = string
}
