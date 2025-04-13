# Fonte de dados para obter informações sobre a identidade da conta AWS atual.
data "aws_caller_identity" "current" {}

# Gera um ID aleatório para ser usado como sufixo nos nomes dos buckets, garantindo unicidade.
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Cria um bucket S3 para armazenar documentos relacionados ao chatbot.
resource "aws_s3_bucket" "docs" {
  bucket = "chatbot-docs-${var.owner_tag}-${random_id.bucket_suffix.hex}" # Nome único do bucket.

  # Tags para identificar e categorizar o bucket.
  tags = merge(
    var.common_tags,
    {
      Name        = "chatbot-docs-${var.owner_tag}"
      Component   = "storage"
      Sensitivity = "high"
    }
  )
}

# Habilita o versionamento no bucket de documentos do chatbot para rastrear versões dos objetos.
resource "aws_s3_bucket_versioning" "docs" {
  bucket = aws_s3_bucket.docs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configura a criptografia no lado do servidor para o bucket de documentos do chatbot usando AES256.
resource "aws_s3_bucket_server_side_encryption_configuration" "docs_encryption" {
  bucket = aws_s3_bucket.docs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloqueia todo o acesso público ao bucket de documentos do chatbot para fins de segurança.
resource "aws_s3_bucket_public_access_block" "docs_block" {
  bucket = aws_s3_bucket.docs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Define uma política de bucket para controlar o acesso ao bucket de documentos do chatbot.
resource "aws_s3_bucket_policy" "docs_access" {
  bucket = aws_s3_bucket.docs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = {
          AWS = var.chatbot_role_arn  # Usando APENAS a variável de input
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          aws_s3_bucket.docs.arn,
          "${aws_s3_bucket.docs.arn}/*"
        ]
      }
    ]
  })
}

# Cria um bucket S3 para armazenar arquivos de estado do Terraform.
resource "aws_s3_bucket" "terraform_state" {
  bucket = "chatbot-terraform-state-${var.owner_tag}-${random_id.bucket_suffix.hex}" # Nome único do bucket.

  # Tags para identificar e categorizar o bucket.
  tags = merge(
    var.common_tags,
    {
      Name        = "Terraform State Bucket"
      Component   = "storage"
      Sensitivity = "critical"
    }
  )
}

# Habilita o versionamento no bucket de estado do Terraform para rastrear versões dos arquivos de estado.
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configura a criptografia no lado do servidor para o bucket de estado do Terraform usando AES256.
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloqueia todo o acesso público ao bucket de estado do Terraform para fins de segurança.
resource "aws_s3_bucket_public_access_block" "terraform_state_block" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cria uma tabela DynamoDB para gerenciar locks do estado do Terraform e evitar modificações simultâneas.
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks-${var.owner_tag}" # Nome único da tabela.
  billing_mode = "PAY_PER_REQUEST" # Modo de cobrança eficiente.
  hash_key     = "LockID" # Chave primária da tabela.

  # Define os atributos da tabela.
  attribute {
    name = "LockID"
    type = "S" # Tipo string.
  }

  # Tags para identificar e categorizar a tabela.
  tags = merge(
    var.common_tags,
    {
      Name      = "Terraform Lock Table"
      Component = "storage"
    }
  )
}