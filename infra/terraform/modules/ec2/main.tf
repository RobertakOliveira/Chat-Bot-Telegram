# Criar a chave SSH
resource "tls_private_key" "generated_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Salvar a chave privada localmente
resource "local_file" "private_key" {
  content          = tls_private_key.generated_key.private_key_pem
  filename         = "${path.module}/ssh_dir/chatbot_key"
  file_permission  = "0600"
}

# Salvar a chave pública localmente
resource "local_file" "public_key" {
  content          = tls_private_key.generated_key.public_key_openssh
  filename         = "${path.module}/ssh_dir/chatbot_key.pub"
  file_permission  = "0644"
}
resource "aws_key_pair" "chatbot_key" {
  key_name   = "chatbot-key"
  public_key = tls_private_key.generated_key.public_key_openssh
}

# Instância EC2
resource "aws_instance" "this" {
  ami                         = var.ami
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  key_name                    = aws_key_pair.chatbot_key.key_name  # Use a chave SSH gerada
  associate_public_ip_address = true

  tags = {
    Name       = "chatbot-instance"
    Project    = "Projeto"
    CostCenter = "CentroDeCusto"
  }

  volume_tags = {
    Name       = "chatbot-volume"
    Project    = "Projeto"
    CostCenter = "CentroDeCusto"
  }

  user_data = <<-EOF
              #!/bin/bash
              pip install --upgrade pip
              pip install -r ../config/requirements.txt

              EOF
}
