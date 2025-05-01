resource "aws_cloudwatch_log_group" "this" {
  name              = var.log_group_name
  retention_in_days = var.retention_in_days

  tags = {
    Project = var.project
  }
}

# Alarmes para CPU
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "chatbot-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "Alarme para alta utilização de CPU"
  alarm_actions      = [var.sns_topic_arn]

  dimensions = {
    InstanceId = var.instance_id
  }
}

# Alarmes para Memória
resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "chatbot-memory-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "mem_used_percent"
  namespace           = "CWAgent"
  period             = "300"
  statistic          = "Average"
  threshold          = "85"
  alarm_description  = "Alarme para alta utilização de memória"
  alarm_actions      = [var.sns_topic_arn]

  dimensions = {
    InstanceId = var.instance_id
  }
}

# Alarmes para Disco
resource "aws_cloudwatch_metric_alarm" "disk_high" {
  alarm_name          = "chatbot-disk-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "Alarme para alta utilização de disco"
  alarm_actions      = [var.sns_topic_arn]

  dimensions = {
    InstanceId = var.instance_id
    path       = "/"
  }
}

# Dashboard do CloudWatch
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "chatbot-dashboard"

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
            ["AWS/EC2", "CPUUtilization", "InstanceId", var.instance_id],
            ["CWAgent", "mem_used_percent", "InstanceId", var.instance_id],
            ["CWAgent", "disk_used_percent", "InstanceId", var.instance_id, "path", "/"]
          ]
          period = 300
          stat   = "Average"
          region = "us-east-1"
          title  = "Métricas Principais"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 6
        width  = 24
        height = 6

        properties = {
          region = "us-east-1"
          title  = "Logs da Aplicação"
          query  = "SOURCE '${var.log_group_name}' | fields @timestamp, @message | sort @timestamp desc | limit 20"
        }
      }
    ]
  })
}
