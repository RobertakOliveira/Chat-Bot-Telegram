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
