

# Criação do bucket S3 para armazenamento de documentos
resource "aws_s3_bucket" "docs" {
  bucket        = "consultor-juridico-${var.environment}-${var.owner_tag}"
  force_destroy = true

  tags = merge(var.common_tags, {
    Name        = "consultor-juridico-${var.owner_tag}",
    Component   = "storage",
    Sensitivity = "high"


  })
}

# Habilitando versionamento no bucket
resource "aws_s3_bucket_versioning" "docs" {
  bucket = aws_s3_bucket.docs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Configurando criptografia do lado do servidor (SSE) no bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "docs" {
  bucket = aws_s3_bucket.docs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloqueando acessos públicos ao bucket S3
resource "aws_s3_bucket_public_access_block" "docs_block" {
  bucket                  = aws_s3_bucket.docs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Definindo a política de acesso ao bucket S3
resource "aws_s3_bucket_policy" "docs_access" {
  bucket = aws_s3_bucket.docs.id
  policy = data.aws_iam_policy_document.docs_bucket_policy.json
}

# Documento de política para o bucket S3
data "aws_iam_policy_document" "docs_bucket_policy" {
  statement {
    sid    = "ForceSSLOnlyAccess"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:*"]
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
      "s3:ListBucket"
    ]
    resources = [
      "${aws_s3_bucket.docs.arn}",
      "${aws_s3_bucket.docs.arn}/*"
    ]
  }
}

# Adicionando arquivos PDF do diretório 'juridicos' para o bucket S3
resource "aws_s3_object" "juridicos" {
  for_each = fileset("${path.module}/../juridicos/", "**/*.pdf")

  bucket = aws_s3_bucket.docs.bucket
  key    = "juridicos/${each.value}"
  source = "${path.module}/../juridicos/${each.value}"
  etag   = filemd5("${path.module}/../juridicos/${each.value}")

  depends_on = [ aws_s3_bucket.docs, aws_s3_bucket_versioning.docs, aws_s3_bucket_server_side_encryption_configuration.docs ]
}