output "lambda_telegram_arn" {
  value = aws_lambda_function.telegram_rag.invoke_arn
}

output "lambda_telegram_name" {
  value = aws_lambda_function.telegram_rag.function_name
}

output "embedding_db_arn" {
  value = aws_lambda_function.embedding_db.arn
}

output "embedding_db_name" {
  value = aws_lambda_function.embedding_db.function_name
}
