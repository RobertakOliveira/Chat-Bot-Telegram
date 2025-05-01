output "docs_bucket_name" {
  description = "Nome do bucket de documentos"
  value       = aws_s3_bucket.docs.id
}

output "docs_bucket_arn" {
  description = "ARN do bucket de documentos"
  value       = aws_s3_bucket.docs.arn
}

output "uploaded_files" {
  value = {
    for k, v in aws_s3_object.juridicos : k => {
      key     = v.key
      version = v.version_id
      etag    = v.etag
    }
  }
}