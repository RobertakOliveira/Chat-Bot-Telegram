output "bucket_name" {
  description = "Nome (ID) do bucket S3 criado."
  value       = aws_s3_bucket.documento_bucket.id
}

output "uploaded_files" {
  description = "Lista de arquivos enviados para o bucket com o prefixo 'juridicos'."
  value       = [for key in keys(aws_s3_object.juridico_folder) : "juridicos/${key}"]
}
