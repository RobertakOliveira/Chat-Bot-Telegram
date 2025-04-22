variable "lambda_functions" {
  type = map(object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  }))
}

variable "ecr_repo_url" {
  type = string
}

variable "exec_role_arn" {
  type = string
}

variable "step_function_arn" {
  type = string
}

resource "null_resource" "build_and_push" {
  for_each = var.lambda_functions

  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region $AWS_REGION | \
        docker login --username AWS --password-stdin ${var.ecr_repo_url}

      docker buildx build --platform linux/amd64 \
        --build-arg LAMBDA_FILE=${each.value.lambda_file} \
        --build-arg HANDLER_NAME=${each.value.handler_name} \
        -t lambda-${each.key} -f ../../Dockerfile .

      docker tag lambda-${each.key}:latest ${var.ecr_repo_url}:${each.value.tag}
      docker push ${var.ecr_repo_url}:${each.value.tag}
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

resource "aws_lambda_function" "lambda1" {
  function_name = "lambda1"
  role          = var.exec_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:${var.lambda_functions["lambda1"].tag}"
  memory_size   = 128
  timeout       = 30

  environment {
    variables = {
      STEP_FUNCTION_ARN = var.step_function_arn
    }
  }

  depends_on = [null_resource.build_and_push]
}

resource "aws_lambda_function" "docker_lambda" {
  for_each = { for k, v in var.lambda_functions : k => v if k != "lambda1" }

  function_name = each.key
  role          = var.exec_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:${each.value.tag}"
  memory_size   = 128
  timeout       = 30

  depends_on = [null_resource.build_and_push]
}

output "lambda1_invoke_arn" {
  value = aws_lambda_function.lambda1.invoke_arn
}

output "lambda1_function_name" {
  value = aws_lambda_function.lambda1.function_name
}

output "lambda_arns" {
  value = merge(
    { lambda1 = aws_lambda_function.lambda1.arn },
    { for k, v in aws_lambda_function.docker_lambda : k => v.arn }
  )
}
