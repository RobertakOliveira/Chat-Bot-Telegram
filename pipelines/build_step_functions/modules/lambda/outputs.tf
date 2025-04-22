output "lambda_arns" {
  description = "ARNs das funções Lambda 2, 3 e 4"
  value = { for k, v in aws_lambda_function.docker_lambda : k => v.arn }
}
