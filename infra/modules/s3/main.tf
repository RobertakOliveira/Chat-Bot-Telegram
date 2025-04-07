resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "docs" {
  bucket = "chatbot-docs-${var.owner_tag}-${random_id.bucket_suffix.hex}"
  
  tags = merge(
    var.common_tags,
    {
      Name      = "chatbot-docs-${var.owner_tag}"
      Component = "storage"
      Sensitivity = "high"
    }
  )
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

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.docs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}