resource "aws_cloudwatch_dashboard" "chatbot_dashboard" {
  dashboard_name = "chatbot-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric",
        x      = 0,
        y      = 0,
        width  = 12,
        height = 6,
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", var.instance_id, { "label" : "CPU Usage" }],
            [".", "NetworkIn", ".", ".", { "label" : "Network In" }],
            [".", "NetworkOut", ".", ".", { "label" : "Network Out" }]
          ],
          view    = "timeSeries",
          stacked = false,
          region  = var.aws_region,
          title   = "EC2 Instance Metrics",
          period  = 300,
          stat    = "Average"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "chatbot-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"
  alarm_description   = "Monitoramento de CPU da instância"
  dimensions = {
    InstanceId = var.instance_id
  }
  tags = var.common_tags
}