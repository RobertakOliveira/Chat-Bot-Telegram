# Data source para buscar a AMI (Amazon Machine Image) mais recente do Ubuntu para instâncias EC2.
data "aws_ami" "ubuntu" {
  most_recent = true

  # Filtro para selecionar a AMI do Ubuntu 22.04 com virtualização HVM.
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  # ID da conta AWS da Canonical (imagens oficiais do Ubuntu).
  owners = ["099720109477"]
}

# Security Group para a instância EC2 do Chatbot.
resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg-${var.environment}"
  description = "Chatbot Security Group"  # Use apenas caracteres ASCII
  vpc_id      = var.vpc_id

  # Permitir acesso SSH de qualquer lugar.
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permitir acesso à API na porta 5000.
  ingress {
    description = "API"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permitir acesso HTTP na porta 80.
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Permitir todo o tráfego de saída.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Role para a instância EC2 do Chatbot.
resource "aws_iam_role" "chatbot_role" {      
  name = "chatbot-role-${var.environment}"

  # Política para permitir que a instância EC2 assuma o papel.
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = merge(
    var.common_tags,
    {
      Name = "Chatbot-Role-${var.environment}"
    }
  )
}

# Política IAM associada ao papel do Chatbot.
resource "aws_iam_role_policy" "chatbot_policy" {
  name = "chatbot-policy-${var.environment}"
  role = aws_iam_role.chatbot_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["bedrock:*"],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = ["s3:*"],
        Effect   = "Allow",
        Resource = [
          "arn:aws:s3:::chatbot-docs-${var.owner_tag}-*",     
          "arn:aws:s3:::chatbot-docs-${var.owner_tag}-*/*"
        ]
      },
      {
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = [
          "ec2:DescribeInstances",
          "ec2:DescribeTags"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

# Perfil de instância IAM para associar o papel à instância EC2.
resource "aws_iam_instance_profile" "chatbot_profile" {
  name = "chatbot-profile-${var.environment}"
  role = aws_iam_role.chatbot_role.name
}

# Par de chaves para acesso SSH à instância EC2.
resource "aws_key_pair" "chatbot_key" {
  key_name   = "chatbot-key-${var.environment}"
  public_key = file("C:/Users/katys/.ssh/terraform_chatbot_key.pub") # Substitua pelo caminho da sua chave pública

  tags = merge(
    var.common_tags,
    {
      Name = "Chatbot-KeyPair-${var.environment}"
    }
  )
}

# Instância EC2 para o Chatbot.
# Substitua o bloco do resource aws_instance por este:
resource "aws_instance" "chatbot_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.chatbot_profile.name
  key_name               = aws_key_pair.chatbot_key.key_name
  user_data              = filebase64("${path.module}/bootstrap.sh")

  # Tags da instância (obrigatórias)
  tags = {
    Name        = "MinhaInstance1"
    Project     = "TerraformTest"
    CostCenter  = "T123"
    Environment = var.environment
    Owner       = var.owner_tag
  }

  # Configuração do disco raiz (sem tags internas)
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    # Removidas as tags daqui
  }

  # Tags aplicadas a TODOS os volumes (incluindo o root)
  volume_tags = {
    Name        = "Example Volume"
    Project     = "MyProject"
    CostCenter  = "C123"
    ManagedBy   = "terraform"
  }
}

# Alarme do CloudWatch para monitorar alta utilização de CPU.
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "chatbot-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"
  alarm_description   = "Monitoramento de CPU da instância do Chatbot"
  dimensions = {
    InstanceId = aws_instance.chatbot_server.id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "Chatbot-CPU-Alarm-${var.environment}"
    }
  )
}

# Dashboard do CloudWatch para monitorar métricas da instância EC2.
resource "aws_cloudwatch_dashboard" "chatbot_dashboard" {
  dashboard_name = "chatbot-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.chatbot_server.id, {"label": "CPU Usage"}],
            [".", "NetworkIn", ".", ".", {"label": "Network In"}],
            [".", "NetworkOut", ".", ".", {"label": "Network Out"}],
            [".", "DiskReadOps", ".", ".", {"label": "Disk Read Ops"}],
            [".", "DiskWriteOps", ".", ".", {"label": "Disk Write Ops"}],
            [".", "StatusCheckFailed", ".", ".", {"label": "Status Checks"}],
            [".", "MemoryUtilization", ".", ".", {"stat": "Average", "period": 60, "label": "Memory Usage"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "EC2 Instance Metrics"
          period  = 300
          stat    = "Average"
        }
      },
      {
        type   = "text"
        x      = 0
        y      = 6
        width  = 12
        height = 3
        properties = {
          markdown = "### Chatbot Jurídico\n**Instance ID:** ${aws_instance.chatbot_server.id}\n**Public IP:** ${aws_instance.chatbot_server.public_ip}\n**Environment:** ${var.environment}\n**Last Updated:** ${timestamp()}"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 9
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/S3", "NumberOfObjects", "StorageType", "AllStorageTypes", "BucketName", module.storage.docs_bucket_name, {"label": "S3 Objects"}],
            [".", "BucketSizeBytes", ".", "StandardStorage", ".", ".", {"label": "S3 Storage"}]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "S3 Storage Metrics"
          period  = 86400
          stat    = "Average"
        }
      }
    ]
  })
}


# Elastic IP para a instância EC2 do Chatbot este recurso auxilia na criação de um IP elástico associado à instância EC2 do Chatbot,
# permitindo que a instância tenha um endereço IP fixo e acessível publicamente.
resource "aws_eip" "chatbot_eip" {
  instance = aws_instance.chatbot_server.id
  tags     = merge(var.common_tags, { Name = "chatbot-eip-${var.environment}" })
}


