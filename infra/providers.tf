# Configuração genérica do provider (sem credenciais) assim não será necessário repetir o provider em cada módulo

provider "aws" {      # O provider AWS é utilizado para interagir com os serviços da AWS.
    
    region = var.aws_region
    # A configuração do provider AWS não deve conter credenciais sensíveis, como access_key e secret_key.

    profile = "sso-poweruser"  # Opcional: se usar AWS SSO
}