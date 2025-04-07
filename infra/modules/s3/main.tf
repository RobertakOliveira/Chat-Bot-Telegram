# Aqui o código do módulo S3:
# # Módulo S3 para criar um bucket S3 com criptografia ativada e políticas de acesso restritas.
# # O módulo também cria uma política de IAM para acesso ao bucket S3.
# # O módulo é configurável através de variáveis de entrada.

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "docs" {
  bucket = "chatbot-docs-${var.owner_tag}-${random_id.bucket_suffix.hex}"
  
  tags = {
    Owner    = var.owner_tag
    Project  = "chatbot-juridico"
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "docs" {
  bucket = aws_s3_bucket.docs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "docs" {
  bucket = aws_s3_bucket.docs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}