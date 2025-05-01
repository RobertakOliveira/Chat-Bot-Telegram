output "instance_id" {
  description = "ID da instância EC2"
  value       = aws_instance.chatbot_server.id
}

output "instance_public_ip" {
  description = "IP público da instância EC2"
  value       = aws_eip.chatbot_eip.public_ip
}

output "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  value       = aws_iam_role.chatbot_role.arn
}

output "security_group_id" {
  description = "ID do Security Group da instância"
  value       = aws_security_group.chatbot_sg.id
}