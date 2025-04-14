# Módulo de Storage para o Chatbot Jurídico
# Versão 2.2 - Com ajustes de política S3 e encriptação AES256

# =============================================
# DATA SOURCES
# =============================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# =============================================
# RANDOM SUFFIX (Para garantir nomes únicos)
# =============================================

resource "random_id" "bucket_suffix" {
  byte_length = 4
  keepers = {
    # Gera novo sufixo se o owner_tag mudar
    owner = var.owner_tag
  }
}

# =============================================
# S3 BUCKET PARA DOCUMENTOS
# =============================================

resource "aws_s3_bucket" "docs" {
  bucket = lower("chatbot-docs-${var.owner_tag}-${random_id.bucket_suffix.hex}")
  
  force_destroy = false  # Previne deleção acidental

  tags = merge(
    var.common_tags,
    {
      Name        = "chatbot-docs-${var.owner_tag}"
      Component   = "storage"
      Sensitivity = "high"
      Compliance  = "confidencial"
    }
  )

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags["CreatedDate"]
    ]
  }
}

resource "aws_s3_object" "pdfs" {
  for_each = fileset(var.dataset_path, "*.pdf") # Pasta local com PDFs
  bucket   = aws_s3_bucket.docs.id
  key      = "juridicos/${each.value}"
  source   = "${var.dataset_path}/${each.value}"
}

# =============================================
# CONFIGURAÇÕES DO BUCKET (AES256)
# =============================================

resource "aws_s3_bucket_versioning" "docs" {
  bucket = aws_s3_bucket.docs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "docs_encryption" {
  bucket = aws_s3_bucket.docs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "docs_block" {
  bucket = aws_s3_bucket.docs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "docs_logging" {
  count = var.enable_access_logging ? 1 : 0

  bucket        = aws_s3_bucket.docs.id
  target_bucket = var.logging_bucket
  target_prefix = "logs/${aws_s3_bucket.docs.id}/"
}

# =============================================
# POLÍTICA DE ACESSO (Bucket Policy) - AJUSTADA
# =============================================

data "aws_iam_policy_document" "bucket_policy" {
  # Bloqueia acesso não HTTPS
  statement {
    sid    = "ForceSSLOnlyAccess"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions   = ["s3:*"]
    resources = [
      "${aws_s3_bucket.docs.arn}",
      "${aws_s3_bucket.docs.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  # Permissões para o Chatbot
  statement {
    sid    = "AllowChatbotAccess"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [var.chatbot_role_arn]
    }
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]
    resources = [
      "${aws_s3_bucket.docs.arn}",
      "${aws_s3_bucket.docs.arn}/*"
    ]
  }

  # Permissões para administradores (opcional - comente se não for necessário)
  # statement {
  #   sid    = "AllowAdminAccess"
  #   effect = "Allow"
  #   principals {
  #     type        = "AWS"
  #     identifiers = var.admin_roles
  #   }
  #   actions    = ["s3:*"]
  #   resources  = [
  #     "${aws_s3_bucket.docs.arn}",
  #     "${aws_s3_bucket.docs.arn}/*"
  #   ]
  # }
}

resource "aws_s3_bucket_policy" "docs_access" {
  bucket = aws_s3_bucket.docs.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}

# =============================================
# DYNAMODB PARA TERRAFORM STATE LOCKING
# =============================================

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks-${var.owner_tag}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = merge(
    var.common_tags,
    {
      Name      = "Terraform Lock Table"
      Component = "state-management"
    }
  )
}

# =============================================
# OUTPUTS
# =============================================

output "docs_bucket_name" {
  description = "Nome do bucket de documentos"
  value       = aws_s3_bucket.docs.id
}

output "docs_bucket_arn" {
  description = "ARN do bucket de documentos"
  value       = aws_s3_bucket.docs.arn
}

output "dynamodb_lock_table" {
  description = "Nome da tabela DynamoDB para locks"
  value       = aws_dynamodb_table.terraform_locks.name
}