# Role para execução do Terraform
resource "aws_iam_role" "terraform_execution_role" {
  name               = "TerraformExecutionRole-Prod"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      }
    }]
  })
}

data "aws_caller_identity" "current" {}

# Política com permissões mínimas para contornar o bloqueio da SCP
resource "aws_iam_policy" "terraform_custom_policy" {
  name        = "TerraformChatbotPolicy-Minimal"
  description = "Permissões mínimas essenciais para provisionamento"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Permissões EC2 mínimas
      {
        Action = [
          "ec2:RunInstances",
          "ec2:DescribeInstances",
          "ec2:CreateTags",
          "ec2:DescribeVolumes"
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      
      # Permissões para S3 (apenas buckets do projeto)
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Effect   = "Allow",
        Resource = [
          "arn:aws:s3:::chatbot-docs-${var.owner_tag}-*",
          "arn:aws:s3:::chatbot-docs-${var.owner_tag}-*/*"
        ]
      },
      
      # Permissões para DynamoDB (apenas tabela de locks)
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/terraform-locks-${var.owner_tag}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "terraform_permissions" {
  role       = aws_iam_role.terraform_execution_role.name
  policy_arn = aws_iam_policy.terraform_custom_policy.arn
}