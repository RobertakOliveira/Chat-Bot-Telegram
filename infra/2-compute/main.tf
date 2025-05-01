

resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg-${var.environment}"
  description = "Security group for EC2 instance with SSM"
  vpc_id      = var.vpc_id

  ingress {   # Nesta parte do código você define as regras de entrada (ingress) para o grupo de segurança, estamos usando ssm para gerenciar a instância
    description = "API"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp" # Permite todos os protocolos
    cidr_blocks = ["0.0.0.0/0"] # Considere restringir em produção
  }

  ingress {  # Nesta parte do código você define as regras de entrada (ingress) para o grupo de segurança, estamos usando ssm para gerenciar a instância
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp" # Permite todos os protocolos
    cidr_blocks = ["0.0.0.0/0"] # Considere restringir em produção
  }

  egress {   
  description = "Egress for SSM services"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"  # Permite todos os protocolos
  cidr_blocks = ["0.0.0.0/0"]

}

 # Regra de saída mais abrangente para permitir todo o tráfego de saída
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Permite todos os protocolos
    cidr_blocks = ["0.0.0.0/0"]
  }

  revoke_rules_on_delete = true
  lifecycle {
    create_before_destroy = true
    ignore_changes = [description]
  }
}

resource "aws_instance" "chatbot_server" {
  ami                    = "ami-084568db4383264d4"  # AMI para Ubuntu 22.04 LTS (verifique se esta AMI é válida na sua região)
  instance_type           = "t2.micro"              # Tipo de instância
  subnet_id               = var.subnet_id
  vpc_security_group_ids  = [aws_security_group.chatbot_sg.id]
  iam_instance_profile    = aws_iam_instance_profile.chatbot_profile.name
  user_data               = filebase64("${path.module}/bootstrap.sh")

  tags = {
    Name        = "Minhainstance1"
    Project     = "Terraformifest"
    CostCenter  = "I123"
    Environment = var.environment
    Owner       = var.owner_tag
    ManagedBy   = "terraform"
  }

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  volume_tags = {
    Name        = "Example Volume"
    Project     = "MyProject"
    CostCenter  = "C123"
    ManagedBy   = "terraform"
    Environment = var.environment
    Owner       = var.owner_tag
  }
}
resource "aws_eip" "chatbot_eip" {
  instance = aws_instance.chatbot_server.id
  tags = merge(var.common_tags, {
    Name = "eip-chatbot-${var.environment}"
  })
}