resource "null_resource" "build_lambda_invoke" {
  provisioner "local-exec" {
    command = <<EOT
    aws ecr get-login-password --region ${var.aws_region} | \
        docker login --username AWS --password-stdin ${var.ecr_repo_url}

    docker buildx build --platform linux/amd64 \
        --build-arg LAMBDA_FILE=${var.lambda_config.lambda_file} \
        --build-arg HANDLER_NAME=${var.lambda_config.handler_name} \
        -t lambda_invoke \
        -f ${path.module}/../../Dockerfile ${path.module}/../..

    docker tag lambda_invoke:latest ${var.ecr_repo_url}:${var.lambda_config.tag}
    docker push ${var.ecr_repo_url}:${var.lambda_config.tag}
    EOT

  }

  triggers = {
    always_run = timestamp()
  }
}

resource "aws_lambda_function" "lambda_invoke" {
  function_name = "lambda_invoke"
  role          = var.exec_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:${var.lambda_config.tag}"
  memory_size   = 128
  timeout       = 30

  environment {
    variables = {
      STEP_FUNCTION_ARN = var.step_function_arn
    }
  }

  depends_on = [null_resource.build_lambda_invoke]
}
