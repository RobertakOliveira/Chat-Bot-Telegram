resource "aws_dynamodb_table" "terraform_state_lock" {
  name         = "terraform-locks-${var.project_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "Terraform State Lock"
    Environment = var.environment
    ManagedBy   = "Terraform"  # Corrigido de "ManageBy" para "ManagedBy"
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "tfstate-${var.project_name}-${var.environment}"
  
  lifecycle {
    prevent_destroy = true
  }

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

output "chatbot_role_arn" {
  value = aws_iam_role.chatbot_role.arn
}