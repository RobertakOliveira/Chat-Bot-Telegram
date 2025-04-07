# Declaração de variáveis para o módulo de infraestrutura (sem variáveis de credenciais)

variable "aws_region" {
    description = "Região da AWS onde os recursos serão criados"
    type       = string  # Tipo da variável: string
    default   = "us-east-1"  # Região padrão da AWS
}

variable "owner_tag" {
    description = "Indentificador do dono (sem dados pessoais)"
    type     = string  # Tipo da variável: string
    default = "katcilane"  # Identificador padrão do dono
    
}