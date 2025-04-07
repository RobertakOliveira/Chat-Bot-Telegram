# Configuração genérica do provider (sem credenciais) assim não será necessário repetir o provider em cada módulo

provider "aws" {
    region = var.aws_region
    # A configuração do provider AWS não deve conter credenciais sensíveis, como access_key e secret_key.
}