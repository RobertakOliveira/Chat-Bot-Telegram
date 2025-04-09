# Based on https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration

# Steps:
# Create the api gateway itself
# Create the methods
# Import the lambdas
# Create the integrations
# Create the deployment
# Create the stage

# Creating API Gateway -----------------------------------------------------------------------------------------------
resource "aws_api_gateway_rest_api" "apigw" {
  name = "chatbot-api"
  description = "A Chatbot for law-related topics."
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Creating Resources (Paths) -----------------------------------------------------------------------------------------
resource "aws_api_gateway_resource" "mainPath" {
    rest_api_id = aws_api_gateway_rest_api.apigw.id
    parent_id = aws_api_gateway_rest_api.apigw.root_resource_id # parent is '/'
    path_part = "qna" #/qna
}

# Creating Methods ---------------------------------------------------------------------------------------------------
resource "aws_api_gateway_method" "mainPath" {
    rest_api_id = aws_api_gateway_rest_api.apigw.id
    resource_id = aws_api_gateway_resource.mainPath.id
    http_method = "POST"
    authorization = "NONE"
}

# Importing Lambdas --------------------------------------------------------------------------------------------------
variable "bucket_name" {
  type = string  
}

module "lambdas" {
    source = "../lambdas"
    bucket_name = var.bucket_name
}

# Creating Integrations (with Lambdas) -------------------------------------------------------------------------------
resource "aws_api_gateway_integration" "mainPath" {
    rest_api_id = aws_api_gateway_rest_api.apigw.id
    resource_id = aws_api_gateway_resource.mainPath.id
    http_method = "POST"
    integration_http_method = "POST"
    type = "AWS_PROXY"
    uri = module.lambdas.mainInvokeARN
    depends_on = [ module.lambdas ]
}

# Creating Deployment
resource "aws_api_gateway_deployment" "apigw_deployment" {
  rest_api_id= aws_api_gateway_rest_api.apigw.id
  depends_on = [ aws_api_gateway_method.mainPath, aws_api_gateway_resource.mainPath, aws_api_gateway_integration.mainPath ]
}

# Creating Stage

variable "stage_name" {
  type = string
}

resource "aws_api_gateway_stage" "apigw_stage" {
  deployment_id = aws_api_gateway_deployment.apigw_deployment.id
  stage_name = var.stage_name
  rest_api_id = aws_api_gateway_rest_api.apigw.id
}