output "lambda_exec_role_arn" {
  description = "ARN da IAM Role de execução da função Lambda"
  value       = aws_iam_role.lambda_exec_role.arn
}

output "step_function_role_arn" {
  description = "ARN da IAM Role de execução da Step Function"
  value       = aws_iam_role.step_function_role.arn
}
