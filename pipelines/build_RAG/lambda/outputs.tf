output "lambda_telegram_arn" {
  value = aws_lambda_function.telegram_rag.invoke_arn
}

output "lambda_telegram_name" {
  value = aws_lambda_function.telegram_rag.function_name
}
