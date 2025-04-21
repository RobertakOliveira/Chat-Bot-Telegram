provider "aws" {
  region = "us-east-1" 
}

variable "lambda_functions" {
  description = "Lista de funções Lambda e seus respectivos arquivos"
  type = map(object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  }))
  default = {
    lambda1 = {
      lambda_file   = "lambda_1.py"
      handler_name  = "handler"
      tag           = "lambda1"
    },
    lambda2 = {
      lambda_file   = "lambda_2.py"
      handler_name  = "handler"
      tag           = "lambda2"
    },
    lambda3 = {
      lambda_file   = "lambda_3.py"
      handler_name  = "handler"
      tag           = "lambda3"
    },
    lambda4 = {
      lambda_file   = "lambda_4.py"
      handler_name  = "handler"
      tag           = "lambda4"
    }
  }
}

# ECR 
resource "aws_ecr_repository" "lambda_ecr" {
  name = "lambda-docker-repo"
  force_delete = true
}

# IAM
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_exec" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Loop para build/push das imagens Docker usando build args
resource "null_resource" "build_and_push" {
  for_each = var.lambda_functions

  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region ${data.aws_region.current.name} | \
        docker login --username AWS --password-stdin ${aws_ecr_repository.lambda_ecr.repository_url}

      docker buildx build --platform linux/amd64 \
        --build-arg LAMBDA_FILE=${each.value.lambda_file} \
        --build-arg HANDLER_NAME=${each.value.handler_name} \
        -t lambda-${each.key} -f Dockerfile .

      docker tag lambda-${each.key}:latest ${aws_ecr_repository.lambda_ecr.repository_url}:${each.value.tag}
      docker push ${aws_ecr_repository.lambda_ecr.repository_url}:${each.value.tag}
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

# Lambda Functions
# Lambda 1 com STEP_FUNCTION_ARN separado
resource "aws_lambda_function" "lambda1" {
  function_name = "lambda1"
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_ecr.repository_url}:${var.lambda_functions["lambda1"].tag}"
  memory_size   = 128
  timeout       = 30

  environment {
    variables = {
      STEP_FUNCTION_ARN = aws_sfn_state_machine.workflow.arn
    }
  }

  depends_on = [null_resource.build_and_push, aws_sfn_state_machine.workflow]
}

# Demais Lambdas
resource "aws_lambda_function" "docker_lambda" {
  for_each = { for k, v in var.lambda_functions : k => v if k != "lambda1" }

  function_name = each.key
  role          = aws_iam_role.lambda_exec_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_ecr.repository_url}:${each.value.tag}"
  memory_size   = 128
  timeout       = 30

  depends_on = [null_resource.build_and_push]
}

# Permissões para API Gateway invocar a lambda1
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda1.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/POST/lambda-entry"
}


# API Gateway REST API
resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "lambda-entry-api"
  protocol_type = "HTTP"
}

# API Integration com Lambda1
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.lambda_api.id
  integration_type       = "AWS_PROXY"
  integration_uri = aws_lambda_function.lambda1.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

# API Route
resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "POST /lambda-entry"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# API Stage
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "$default"
  auto_deploy = true
}

# Step Function IAM Role
resource "aws_iam_role" "step_function_role" {
  name = "step-function-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "states.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "step_function_policy" {
  name = "step-function-policy"
  role = aws_iam_role.step_function_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [for name, lambda in merge(aws_lambda_function.docker_lambda, { lambda1 = aws_lambda_function.lambda1 }) : {
      Effect   = "Allow",
      Action   = ["lambda:InvokeFunction"],
      Resource = lambda.arn
    }]
  })
}

# Step Function com as 4 Lambdas encadeadas
resource "aws_sfn_state_machine" "workflow" {
  name     = "lambda-docker-workflow"
  role_arn = aws_iam_role.step_function_role.arn

  definition = jsonencode({
    StartAt = "lambda2",
    States = {
      lambda2 = {
        Type     = "Task",
        Resource = aws_lambda_function.docker_lambda["lambda2"].arn,
        Next     = "lambda3"
      },
      lambda3 = {
        Type     = "Task",
        Resource = aws_lambda_function.docker_lambda["lambda3"].arn,
        Next     = "lambda4"
      },
      lambda4 = {
        Type     = "Task",
        Resource = aws_lambda_function.docker_lambda["lambda4"].arn,
        End      = true
      }
    }
  })
}

# Lambda1 execução da Step Function
resource "aws_iam_policy" "lambda1_step_exec" {
  name = "lambda1-step-exec"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = ["states:StartExecution"],
      Resource = aws_sfn_state_machine.workflow.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda1_exec_step_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda1_step_exec.arn
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
