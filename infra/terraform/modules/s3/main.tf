resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "documento_bucket" {
  bucket = "${var.bucket_name_prefix}-${random_string.bucket_suffix.result}"

  tags = {
    Name         = var.bucket_tag_name
    Project      = var.project
    CostCenter   = var.cost_center
    ResourceType = "s3-bucket"
  }
}

resource "aws_s3_bucket_versioning" "documento_bucket_versioning" {
  bucket = aws_s3_bucket.documento_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documento_bucket_encryption" {
  bucket = aws_s3_bucket.documento_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Upload único arquivo ZIP
resource "aws_s3_object" "juridico_zip" {
  count  = var.upload_zip ? 1 : 0  

  bucket = aws_s3_bucket.documento_bucket.id
  key    = "juridicos.zip"
  source = var.dataset_path
  etag   = filemd5(var.dataset_path)
}

