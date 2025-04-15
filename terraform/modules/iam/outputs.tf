output "role_arn" {
  description = "ARN da IAM Role criada"
  value       = aws_iam_role.role.arn
}
