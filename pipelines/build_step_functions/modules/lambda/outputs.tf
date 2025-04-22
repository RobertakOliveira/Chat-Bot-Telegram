output "lambda1_invoke_arn" {
  description = "ARN de invocação da função Lambda 1"
  value       = aws_lambda_function.lambda1.invoke_arn
}

output "lambda1_function_name" {
  description = "Nome da função Lambda 1"
  value       = aws_lambda_function.lambda1.function_name
}

output "lambda_arns" {
  description = "Mapeamento com ARN de todas as funções Lambda"
  value = merge(
    { lambda1 = aws_lambda_function.lambda1.arn },
    { for k, v in aws_lambda_function.docker_lambda : k => v.arn }
  )
}
