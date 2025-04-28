output "vpc_id" {
  description = "ID da VPC criada"
  value       = aws_vpc.this.id
}

output "public_subnet_id" {
  description = "ID da subnet pública criada"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "ID do security group para SSH/HTTP/HTTPS"
  value       = aws_security_group.allow_ssh.id
}

output "default_security_group_id" {
  description = "ID do security group default"
  value       = aws_default_security_group.default.id
}
