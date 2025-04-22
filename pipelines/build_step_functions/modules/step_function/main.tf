variable "role_arn" {
  type = string
}

variable "lambda_arns" {
  type = map(string)
}

resource "aws_sfn_state_machine" "workflow" {
  name     = "lambda-docker-workflow"
  role_arn = var.role_arn

  definition = jsonencode({
    StartAt = "lambda2",
    States = {
      lambda2 = {
        Type     = "Task",
        Resource = var.lambda_arns["lambda2"],
        Next     = "lambda3"
      },
      lambda3 = {
        Type     = "Task",
        Resource = var.lambda_arns["lambda3"],
        Next     = "lambda4"
      },
      lambda4 = {
        Type     = "Task",
        Resource = var.lambda_arns["lambda4"],
        End      = true
      }
    }
  })
}

output "workflow_arn" {
  value = aws_sfn_state_machine.workflow.arn
}
