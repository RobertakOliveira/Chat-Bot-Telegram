variable "lambda_telegram_arn" {
  description = "ARN de invocação da Lambda Telegram"
  type        = string
}

variable "lambda_telegram_name" {
  description = "Nome da Lambda Telegram"
  type        = string
}

variable "embedding_db_arn" {
  description = "ARN da Lambda que gera embeddings"
  type        = string
}

variable "embedding_db_name" {
  description = "Nome da Lambda que gera embeddings"
  type        = string
}
