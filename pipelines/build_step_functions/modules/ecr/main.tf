resource "aws_ecr_repository" "lambda_ecr" {
  name          = "lambda-docker-repo"
  force_delete  = true
}

output "repository_url" {
  value = aws_ecr_repository.lambda_ecr.repository_url
}
