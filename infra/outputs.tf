# infra/outputs.tf

output "chatbot_instance_public_ip" {
  description = "Public IP address of the Chatbot EC2 instance"
  value       = module.compute.instance_public_ip
}

output "chatbot_instance_id" {
  description = "ID of the Chatbot EC2 instance"
  value       = module.compute.instance_id
}

output "chatbot_security_group_id" {
  description = "ID of the Chatbot Security Group"
  value       = module.compute.security_group_id
}