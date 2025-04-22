variable "lambda_functions" {
  description = "Mapeamento das funções Lambda e seus arquivos Docker"
  type = map(object({
    lambda_file   = string
    handler_name  = string
    tag           = string
  }))
}

variable "ecr_repo_url" {
  description = "URL do repositório ECR"
  type        = string
}

variable "exec_role_arn" {
  description = "ARN da IAM Role de execução das Lambdas"
  type        = string
}

variable "step_function_arn" {
  description = "ARN da Step Function (usado na Lambda 1)"
  type        = string
}
