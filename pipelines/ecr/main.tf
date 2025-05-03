resource "aws_ecr_repository" "lambda_ecr" {
  name          = "lambda-docker-repo"
  force_delete  = true
}