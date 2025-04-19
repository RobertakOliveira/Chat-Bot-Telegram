output "log_group_name" {
  description = "Nome do Log Group criado"
  value       = aws_cloudwatch_log_group.this.name
}
