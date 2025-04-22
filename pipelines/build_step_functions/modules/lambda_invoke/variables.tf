variable "lambda_config" {
  type = object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  })
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

variable "aws_region" {
  type        = string
  description = "Região AWS para autenticação no ECR"
}
