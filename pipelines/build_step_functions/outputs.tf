output "api_gateway_url" {
  description = "URL pública do endpoint da API Gateway para invocar a Lambda 1"
  value       = module.apigateway.api_url
}

output "lambda1_invoke_arn" {
  description = "ARN de invocação da Lambda 1"
  value       = module.lambda.lambda1_invoke_arn
}

output "step_function_arn" {
  description = "ARN da Step Function que orquestra as 4 Lambdas"
  value       = module.step_function.workflow_arn
}

output "lambda_arns" {
  description = "ARNs de todas as funções Lambda disponíveis"
  value       = module.lambda.lambda_arns
}