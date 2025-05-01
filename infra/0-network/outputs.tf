output "vpc_id" {
  description = "ID da VPC criada"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID da Subnet Pública"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "ID do Security Group padrão"
  value       = aws_vpc.main.default_security_group_id
}