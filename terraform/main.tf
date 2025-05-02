provider "aws" {
  region = "us-east-1"  # ou sua região preferida
  profile = "simonesantos"
}

# Manter todos os recursos de VPC
resource "aws_vpc" "jusbot_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true
  
  tags = {
    Name        = "JusBot-VPC"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Subnet pública para o EC2
resource "aws_subnet" "jusbot_public_subnet" {
  vpc_id            = aws_vpc.jusbot_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"  # Ajuste conforme sua região
  map_public_ip_on_launch = true
  
  tags = {
    Name        = "JusBot-Public-Subnet"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Subnet privada para recursos internos
resource "aws_subnet" "jusbot_private_subnet" {
  vpc_id            = aws_vpc.jusbot_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"  # Use uma AZ diferente para maior disponibilidade
  
  tags = {
    Name        = "JusBot-Private-Subnet"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Internet Gateway para acesso à internet
resource "aws_internet_gateway" "jusbot_igw" {
  vpc_id = aws_vpc.jusbot_vpc.id
  
  tags = {
    Name        = "JusBot-IGW"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Tabela de rotas para a subnet pública
resource "aws_route_table" "jusbot_public_rt" {
  vpc_id = aws_vpc.jusbot_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.jusbot_igw.id
  }
  
  tags = {
    Name        = "JusBot-Public-RT"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Associação da tabela de rotas com a subnet pública
resource "aws_route_table_association" "jusbot_public_rta" {
  subnet_id      = aws_subnet.jusbot_public_subnet.id
  route_table_id = aws_route_table.jusbot_public_rt.id
}

# NAT Gateway para que recursos na subnet privada acessem a internet
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  
  tags = {
    Name        = "JusBot-NAT-EIP"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

resource "aws_nat_gateway" "jusbot_nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.jusbot_public_subnet.id
  
  tags = {
    Name        = "JusBot-NAT"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
  
  depends_on = [aws_internet_gateway.jusbot_igw]
}

# Tabela de rotas para a subnet privada
resource "aws_route_table" "jusbot_private_rt" {
  vpc_id = aws_vpc.jusbot_vpc.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.jusbot_nat.id
  }
  
  tags = {
    Name        = "JusBot-Private-RT"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Associação da tabela de rotas com a subnet privada
resource "aws_route_table_association" "jusbot_private_rta" {
  subnet_id      = aws_subnet.jusbot_private_subnet.id
  route_table_id = aws_route_table.jusbot_private_rt.id
}

# VPC Endpoint para S3 (permite acesso ao S3 sem sair da VPC)
resource "aws_vpc_endpoint" "s3_endpoint" {
  vpc_id          = aws_vpc.jusbot_vpc.id
  service_name    = "com.amazonaws.us-east-1.s3"
  route_table_ids = [aws_route_table.jusbot_private_rt.id, aws_route_table.jusbot_public_rt.id]
  
  tags = {
    Name        = "JusBot-S3-Endpoint"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# VPC Endpoint para Bedrock (permite acesso ao Bedrock sem sair da VPC)
resource "aws_vpc_endpoint" "bedrock_endpoint" {
  vpc_id             = aws_vpc.jusbot_vpc.id
  service_name       = "com.amazonaws.us-east-1.bedrock-runtime"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [aws_subnet.jusbot_private_subnet.id]
  security_group_ids = [aws_security_group.jusbot_sg.id]
  private_dns_enabled = true
  
  tags = {
    Name        = "JusBot-Bedrock-Endpoint"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Grupo de segurança para a instância EC2
resource "aws_security_group" "jusbot_sg" {
  name        = "jusbot-security-group"
  description = "Permite trafego necessario para JusBot"
  vpc_id      = aws_vpc.jusbot_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Recomendado: restrinja para seu IP apenas
    description = "SSH para gerenciamento"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Porta para API personalizada
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "API do JusBot"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Todo trafego de saida"
  }
  
  tags = {
    Name        = "JusBot-SG"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# IAM Role para a instância EC2
resource "aws_iam_role" "jusbot_role" {
  name = "jusbot-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "JusBot-IAM-Role"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Políticas para a IAM Role
resource "aws_iam_role_policy_attachment" "s3_full_access" {
  role       = aws_iam_role.jusbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "bedrock_access" {
  role       = aws_iam_role.jusbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_access" {
  role       = aws_iam_role.jusbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

# Perfil de instância para associar a Role à instância EC2
# O perfil de instância já existe, então vamos referenciar com data source
data "aws_iam_instance_profile" "jusbot_profile" {
  name = "jusbot-profile"
}

# API Gateway
resource "aws_api_gateway_rest_api" "jusbot_api" {
  name        = "jusbot-api"
  description = "API Gateway para JusBot"
  
  tags = {
    Name        = "JusBot-API-Gateway"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# Recurso do API Gateway
resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.jusbot_api.id
  parent_id   = aws_api_gateway_rest_api.jusbot_api.root_resource_id
  path_part   = "webhook"
}

# Método HTTP para o API Gateway
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.jusbot_api.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

# Variável para IP do EC2 (a ser substituída após a criação manual da instância)
variable "ec2_ip" {
  description = "IP da instância EC2 que será criada manualmente"
  type        = string
  default     = "0.0.0.0"  # Valor padrão, deve ser atualizado após a criação da EC2
}

# Integração HTTP com o EC2
resource "aws_api_gateway_integration" "ec2_integration" {
  rest_api_id = aws_api_gateway_rest_api.jusbot_api.id
  resource_id = aws_api_gateway_resource.webhook.id
  http_method = aws_api_gateway_method.webhook_post.http_method

  integration_http_method = "POST"
  type                    = "HTTP"
  uri                     = "http://${var.ec2_ip}:8080/webhook"
  
  # Timeout e configuração de conexão
  connection_type = "INTERNET"
  timeout_milliseconds = 29000  # 29 segundos
}

# Respostas do método
resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.jusbot_api.id
  resource_id = aws_api_gateway_resource.webhook.id
  http_method = aws_api_gateway_method.webhook_post.http_method
  status_code = "200"
}

# Respostas da integração
resource "aws_api_gateway_integration_response" "integration_response" {
  rest_api_id = aws_api_gateway_rest_api.jusbot_api.id
  resource_id = aws_api_gateway_resource.webhook.id
  http_method = aws_api_gateway_method.webhook_post.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
  
  depends_on = [
    aws_api_gateway_integration.ec2_integration
  ]
}

# Deployment do API Gateway
resource "aws_api_gateway_deployment" "jusbot_deploy" {
  depends_on = [
    aws_api_gateway_integration.ec2_integration,
    aws_api_gateway_integration_response.integration_response
  ]

  rest_api_id = aws_api_gateway_rest_api.jusbot_api.id
  
  lifecycle {
    create_before_destroy = true
  }
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.ec2_integration.id
    ]))
  }
}

# Stage do API Gateway
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.jusbot_deploy.id
  rest_api_id   = aws_api_gateway_rest_api.jusbot_api.id
  stage_name    = "prod"
  
  tags = {
    Name        = "JusBot-API-Stage"
    Project     = "JusBot"
    CostCenter  = "TI-IA"
  }
}

# CloudWatch Log Group para EC2
# O Cloudwatch log group já existe, então vamos referenciar com data source
data "aws_cloudwatch_log_group" "jusbot_logs" {
  name = "/jusbot/ec2-logs"
}

# Variáveis
variable "telegram_token" {
  description = "Token do bot do Telegram"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "Região AWS a ser usada"
  type        = string
  default     = "us-east-1"
}

# Outputs
output "vpc_id" {
  value = aws_vpc.jusbot_vpc.id
  description = "ID da VPC criada"
}

output "security_group_id" {
  value = aws_security_group.jusbot_sg.id
  description = "ID do grupo de segurança para a EC2"
}

output "public_subnet_id" {
  value = aws_subnet.jusbot_public_subnet.id
  description = "ID da subnet pública para a EC2"
}

output "ec2_instance_profile" {
  value = data.aws_iam_instance_profile.jusbot_profile.name
  description = "Nome do perfil de instancia para a EC2"
}

output "api_gateway_url" {
  value = "${aws_api_gateway_stage.prod.invoke_url}/webhook"
  description = "URL do endpoint do API Gateway para configurar webhook do Telegram"
}
