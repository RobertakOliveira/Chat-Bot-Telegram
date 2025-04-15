output "api_id" {
  description = "ID do API Gateway criado"
  value       = aws_api_gateway_rest_api.api.id
}

output "invoke_url" {
  description = "URL para invocar a API no stage configurado"
  value       = aws_api_gateway_deployment.deployment.invoke_url
}
