output "log_group_name" {
  description = "Nome do Log Group criado"
  value       = aws_cloudwatch_log_group.this.name
}

output "sns_topic_arn" {
  description = "ARN do tópico SNS usado para alarmes"
  value       = var.sns_topic_arn
}
