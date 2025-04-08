# Modulo VPC para o projeto Chatbot
# Este módulo cria uma VPC e sub-rede pública para o projeto Chatbot.


resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.common_tags,
    {
      Name = "vpc-chatbot-${var.environment}"  # Corrigido: ${} em vez de $[]
    }
  )
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 1)  # Corrigido: função cidrsubnet
  availability_zone = "${var.aws_region}a"  # Corrigido: ${} e sintaxe AZ

  tags = merge(
    var.common_tags, 
    { 
      Name = "subnet-public-${var.environment}" 
    }
  )
}