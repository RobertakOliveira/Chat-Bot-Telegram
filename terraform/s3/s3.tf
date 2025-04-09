variable "bucket_name" {
  type = string
}

resource "aws_s3_bucket" "chatbot-s3" {
  bucket = var.bucket_name
}

output "bucket_name" {
    value = var.bucket_name
}