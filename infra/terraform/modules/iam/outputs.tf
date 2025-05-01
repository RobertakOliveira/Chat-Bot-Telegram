output "role_arn" {
  description = "ARN da IAM Role criada"
  value       = aws_iam_role.role.arn
}

output "role_name" {
  description = "Nome da IAM Role criada"
  value       = aws_iam_role.role.name
}

output "instance_profile_name" {
  description = "Nome do IAM Instance Profile criado"
  value       = aws_iam_instance_profile.ec2_profile.name
}
