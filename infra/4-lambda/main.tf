resource "aws_lambda_function" "start_ec2" {
  filename      = "${path.module}/start_ec2.zip"
  function_name = "start_ec2_instances_${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "ec2_start.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300

  environment {
    variables = {
      PROJECT_TAG = var.project_name
    }
  }

  tags = merge(var.common_tags, {
    Name = "start-ec2-lambda-${var.environment}"
  })
}

resource "aws_lambda_function" "stop_ec2" {
  filename      = "${path.module}/stop_ec2.zip"
  function_name = "stop_ec2_instances_${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "ec2_stop.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300

  environment {
    variables = {
      PROJECT_TAG = var.project_name
    }
  }

  tags = merge(var.common_tags, {
    Name = "stop-ec2-lambda-${var.environment}"
  })
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = merge(var.common_tags, {
    Name = "lambda-exec-role-${var.environment}"
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_ec2_access" {
  name = "lambda_ec2_access_${var.environment}"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ec2:Describe*",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ],
        Resource = "*"
      }
    ]
  })
}