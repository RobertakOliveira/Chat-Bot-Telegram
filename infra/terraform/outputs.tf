output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.vpc.vpc_id
}

output "s3_bucket_name" {
  description = "Nome do bucket S3 criado"
  value       = module.s3.bucket_name
}

output "s3_uploaded_files" {
  description = "Lista de arquivos enviados para o bucket S3"
  value       = module.s3.uploaded_files
}

output "ec2_instance_id" {
  description = "ID da instância EC2"
  value       = module.ec2.instance_id
}

output "cloudwatch_log_group" {
  description = "Nome do Log Group criado no CloudWatch"
  value       = module.cloudwatch.log_group_name
}

output "api_gateway_id" {
  description = "ID do API Gateway criado"
  value       = module.api_gateway.api_id
}

output "api_invoke_url" {
  description = "URL para invocar a API Gateway"
  value       = module.api_gateway.invoke_url
}

output "iam_role_arn" {
  description = "ARN da IAM Role criada"
  value       = module.iam.role_arn
}
