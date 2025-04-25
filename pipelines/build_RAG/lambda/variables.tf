variable "lambda_config" {
  description = "Configuração da Lambda única"
  type = object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  })
}

variable "ecr_repo_url" {
  description = "URL do repositório ECR"
  type        = string
}

variable "exec_role_arn" {
  description = "ARN da IAM Role de execução da Lambda"
  type        = string
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
}
