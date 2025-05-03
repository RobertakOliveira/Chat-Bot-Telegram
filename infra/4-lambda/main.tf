# Função Lambda: Iniciar EC2
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

# Função Lambda: Parar EC2
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

# Role IAM para as Lambdas
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

# Política básica de execução da Lambda
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Permissões para EC2 (START/STOP/DESCRIBE)
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

# Permissões extras para EventBridge e CloudTrail
resource "aws_iam_role_policy" "lambda_ec2_access_extra" {
  name = "lambda_extra_eventbridge_access_${var.environment}"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cloudtrail:LookupEvents",
          "events:PutRule",
          "events:PutTargets"
        ],
        Resource = "*"
      }
    ]
  })
}

# Regra do EventBridge para acionar Lambda quando EC2 for criada
resource "aws_cloudwatch_event_rule" "ec2_created" {
  name        = "trigger-lambda-on-ec2-creation-${var.environment}"
  description = "Dispara a Lambda quando uma EC2 do chatbot é criada"

  event_pattern = jsonencode({
    source      = ["aws.ec2"],
    "detail-type" = ["AWS API Call via CloudTrail"],
    detail = {
      eventName = ["RunInstances"],
      responseElements = {
        instancesSet = {
          items = [{
            tags = {
              items = [{
                key   = ["Project"],
                value = [var.project_name]
              }]
            }
          }]
        }
      }
    }
  })
}

# Destino do EventBridge → Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.ec2_created.name
  target_id = "start-ec2-lambda"
  arn       = aws_lambda_function.start_ec2.arn
}

# Permissão para EventBridge invocar a Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_ec2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_created.arn
}
