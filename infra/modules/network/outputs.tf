# Essa parte significa que o código está criando uma política IAM com permissões mínimas necessárias para acessar o serviço Bedrock e um bucket S3 específico. 
# O nome da política inclui um sufixo aleatório para garantir que seja único. A política é definida em formato JSON, especificando as ações permitidas
# e os recursos aos quais essas ações se aplicam.

# modules/network/outputs.tf (mantenha apenas este)
# Outputs melhorados
output "vpc_id" {
  description = "ID da VPC"
  value       = aws_vpc.main.id
  # Garanta que o valor não seja null
  precondition {
    condition     = aws_vpc.main.id != null
    error_message = "VPC ID não pode ser null"
  }
}

output "public_subnet_id" {
  description = "ID da Subnet Pública"
  value       = aws_subnet.public.id
  precondition {
    condition     = aws_subnet.public.id != null
    error_message = "Subnet ID não pode ser null"
  }
}