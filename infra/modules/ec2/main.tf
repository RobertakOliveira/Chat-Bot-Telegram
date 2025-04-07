## Recursos com tags + random suffixes, significa que os recursos criados terão sufixos aleatórios adicionados aos seus nomes.
# # Isso é importante para garantir que os recursos sejam únicos e evitar conflitos de nomes.

# Módulo EC2 - Recursos para instâncias EC2 do Chatbot Jurídico

# Sufixo único para recursos EC2 (não para S3)
resource "random_id" "ec2_suffix" {
  byte_length = 4
}

# Instância EC2 principal
resource "aws_instance" "chatbot_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  # Nome único para a instância
  tags = merge(
    var.common_tags,
    {
      Name    = "chatbot-server-${random_id.ec2_suffix.hex}"
      Owner   = var.owner_tag
      Service = "application"
    }
  )
}

# Security Group específico
resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg-${random_id.ec2_suffix.hex}"
  description = "Security Group para o Chatbot Jurídico"

  tags = merge(
    var.common_tags,
    {
     Component = "security"
    }
  )
}