# Data source para buscar a AMI (Amazon Machine Image) mais recente do Ubuntu para instâncias EC2.
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

# Security Group para a instância EC2 do Chatbot.
resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg-${var.environment}"
  description = "Chatbot Security Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "API"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

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

# Permissões SSM
resource "aws_iam_role_policy_attachment" "ssm_managed_instance" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ssm_directory_access" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMDirectoryServiceAccess"
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

# Perfil de instância IAM
resource "aws_iam_instance_profile" "chatbot_profile" {
  name = "chatbot-profile-${var.environment}"
  role = aws_iam_role.chatbot_role.name
}

# Instância EC2 para o Chatbot (sem SSH, com SSM)
resource "aws_instance" "chatbot_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.chatbot_profile.name
  user_data              = filebase64("${path.module}/bootstrap.sh")

  tags = {
    Name        = "MinhaInstance1"
    Project     = "TerraformTest"
    CostCenter  = "T123"
    Environment = var.environment
    Owner       = var.owner_tag
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
  }
}

# Alarme do CloudWatch para uso de CPU
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

# Dashboard do CloudWatch
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
            [".", "DiskWriteOps", ".", ".", {"label": "Disk Write Ops"}]
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
          markdown = "### Chatbot Jurídico\n**Instance ID:** ${aws_instance.chatbot_server.id}\n**Public IP:** ${aws_instance.chatbot_server.public_ip}"
        }
      }
    ]
  })
}

# Elastic IP para a instância EC2 do Chatbot
resource "aws_eip" "chatbot_eip" {
  instance = aws_instance.chatbot_server.id
  tags     = merge(var.common_tags, { Name = "chatbot-eip-${var.environment}" })
}
