output "dashboard_url" {
  description = "URL do Dashboard CloudWatch"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=chatbot-dashboard-${var.environment}"
}