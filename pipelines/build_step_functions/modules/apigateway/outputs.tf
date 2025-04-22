output "api_url" {
  description = "Endpoint público da API Gateway"
  value       = "${aws_apigatewayv2_api.lambda_api.api_endpoint}/lambda-entry"
}

output "execution_arn" {
  description = "ARN usado para configurar permissões de invocação na Lambda"
  value       = aws_apigatewayv2_api.lambda_api.execution_arn
}
