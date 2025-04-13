## Recursos com tags + random suffixes, significa que os recursos criados terão sufixos aleatórios adicionados aos seus nomes.
# # Isso é importante para garantir que os recursos sejam únicos e evitar conflitos de nomes.

# Módulo EC2 - Recursos para instâncias EC2 do Chatbot Jurídico

# Sufixo único para recursos EC2 (não para S3)
resource "aws_instance" "chatbot_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]
  key_name               = aws_key_pair.chatbot_key.key_name
  user_data              = filebase64("${path.module}/bootstrap.sh")

  tags = merge(
    var.common_tags,
    {
      Name      = "chatbot-server-${var.environment}"
      Component = "application"
    }
  )
}

resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg-${var.environment}"
  description = "Security Group para o Chatbot Jurídico"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrinja isso para seu IP em produção
  }

  ingress {
    from_port   = 5000 # Porta da API Flask
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, { Component = "security" })
}

resource "aws_key_pair" "chatbot_key" {
  key_name   = "chatbot-key-${var.environment}"
  public_key = file("~/.ssh/chatbot_key.pub") # Gere antes com ssh-keygen
}