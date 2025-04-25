output "lambda_telegram_arn" {
  description = "ARN de invocação da Lambda Telegram"
  value       = aws_lambda_function.telegram_RAG.invoke_arn
}

output "lambda_telegram_name" {
  description = "Nome da função Lambda Telegram"
  value       = aws_lambda_function.telegram_RAG.function_name
}
