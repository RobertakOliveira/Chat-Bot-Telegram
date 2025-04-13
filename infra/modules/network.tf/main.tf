# Recurso que cria uma VPC (Virtual Private Cloud) na AWS
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr # Define o bloco CIDR da VPC
  enable_dns_support   = true         # Habilita suporte a DNS na VPC
  enable_dns_hostnames = true         # Habilita nomes DNS para instâncias na VPC

  tags = merge(
    var.common_tags,
    {
      Name = "vpc-chatbot-${var.environment}"
    }
  )
}

# Recurso que cria uma Subnet pública
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 1)
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true  # Associa IP público automaticamente às instâncias
  
  tags = merge(
    var.common_tags,
    {
      Name = "subnet-public-${var.environment}"
    }
  )
}

# Recurso que cria um Internet Gateway para permitir acesso à internet
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "igw-chatbot-${var.environment}"
    }
  )
}

# Recurso que cria uma Tabela de Rotas pública
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "rt-public-${var.environment}"
    }
  )
}

# Recurso que associa a Subnet pública à Tabela de Rotas pública
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}