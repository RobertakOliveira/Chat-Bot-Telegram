output "private_key_pem" {
  value     = tls_private_key.generated_key.private_key_pem
  sensitive = true
}

output "instance_id" {
  description = "ID da instância EC2"
  value       = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}
