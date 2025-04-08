# Esse arquivo contém a definição do módulo VPC, que cria uma VPC com sub-redes públicas e privadas.
# O módulo é configurado para ser reutilizável e parametrizável, permitindo que diferentes ambientes sejam criados com facilidade.

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.common_tags,
    {
      Name = "vpc-chatbot-${var.environment}"
    }
  )
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 1)
  availability_zone = "${var.aws_region}a"

  tags = merge(var.common_tags, { Name = "subnet-public-${var.environment}" })
}