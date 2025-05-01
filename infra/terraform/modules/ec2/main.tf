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
  key_name                    = aws_key_pair.chatbot_key.key_name  
  associate_public_ip_address = true
  iam_instance_profile        = var.iam_instance_profile_name

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
            # Instalar o agente do CloudWatch
            sudo yum install -y amazon-cloudwatch-agent

            # Criar arquivo de configuração
            cat <<'CONFIG' > /tmp/amazon-cloudwatch-agent.json
            {
              "logs": {
                "logs_collected": {
                  "files": {
                    "collect_list": [
                      {
                        "file_path": "/var/log/messages",
                        "log_group_name": "${var.log_group_name}",
                        "log_stream_name": "{instance_id}"
                      },
                      {
                        "file_path": "/var/log/cloud-init-output.log",
                        "log_group_name": "${var.log_group_name}",
                        "log_stream_name": "{instance_id}"
                      },
                      {
                        "file_path": "/var/log/chatbot.log",
                        "log_group_name": "${var.log_group_name}",
                        "log_stream_name": "{instance_id}-chatbot"
                      }
                    ]
                  }
                }
              },
              "metrics": {
                "metrics_collected": {
                  "cpu": {
                    "resources": ["*"],
                    "measurement": [
                      "cpu_usage_idle",
                      "cpu_usage_iowait",
                      "cpu_usage_user",
                      "cpu_usage_system"
                    ],
                    "totalcpu": true
                  },
                  "disk": {
                    "resources": ["/"],
                    "measurement": [
                      "used_percent"
                    ]
                  },
                  "mem": {
                    "measurement": [
                      "mem_used_percent"
                    ]
                  }
                }
              }
            }
            CONFIG

            # Mover o arquivo de configuração para o local correto
            sudo mv /tmp/amazon-cloudwatch-agent.json /opt/aws/amazon-cloudwatch-agent/etc/

            # Iniciar o agente
            sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s
            sudo systemctl start amazon-cloudwatch-agent
            sudo systemctl enable amazon-cloudwatch-agent

            # Criar diretório para logs do chatbot
            sudo mkdir -p /var/log/chatbot
            sudo touch /var/log/chatbot.log
            sudo chmod 666 /var/log/chatbot.log

            # Seus outros comandos
            pip install --upgrade pip
            pip install -r ../config/requirements.txt
            EOF
}