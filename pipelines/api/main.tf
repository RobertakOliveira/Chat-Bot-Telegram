resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "oabot-juridico"
  protocol_type = "HTTP"
}

# Integração da Lambda telegram_RAG
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.lambda_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.lambda_telegram_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "POST /webhook"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Integração da Lambda embedding_db
resource "aws_apigatewayv2_integration" "embedding_integration" {
  api_id                 = aws_apigatewayv2_api.lambda_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.embedding_db_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "embedding_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "POST /generateEmbeddings"
  target    = "integrations/${aws_apigatewayv2_integration.embedding_integration.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "$default"
  auto_deploy = true
}

# Permissões da API Gateway → Lambda telegram_RAG
resource "aws_lambda_permission" "apigw_telegram" {
  statement_id  = "AllowAPIGatewayInvokeTelegram"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_telegram_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/POST/webhook"
}

# Permissões da API Gateway → Lambda embedding_db
resource "aws_lambda_permission" "apigw_embedding" {
  statement_id  = "AllowAPIGatewayInvokeEmbedding"
  action        = "lambda:InvokeFunction"
  function_name = var.embedding_db_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/POST/generateEmbeddings"
}
