
# Outputs do módulo ec2 que exibem informações sobre os recursos criados.


output "chatbot_role_arn" {
  description = "ARN da IAM Role do Chatbot"
  value       = aws_iam_role.chatbot_role.arn
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_eip.chatbot_eip.public_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.chatbot_server.id
}

output "security_group_id" {
  description = "ID of the Security Group"
  value       = aws_security_group.chatbot_sg.id
}