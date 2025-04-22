output "repository_url" {
  description = "URL do repositório ECR para as imagens Docker"
  value       = aws_ecr_repository.lambda_ecr.repository_url
}
