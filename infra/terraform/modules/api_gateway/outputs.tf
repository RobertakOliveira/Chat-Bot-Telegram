output "api_id" {
  description = "ID do API Gateway criado"
  value       = aws_api_gateway_rest_api.api.id
}

output "invoke_url" {
  description = "URL de invocação da API"
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.stage.stage_name}/${aws_api_gateway_resource.proxy.path_part}"
}
