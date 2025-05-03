resource "aws_s3_bucket" "rag_data" {
  bucket         = "rag-data-telegram-team-5"
  force_destroy  = true
}

resource "aws_s3_object" "input_folder" {
  bucket = aws_s3_bucket.rag_data.bucket
  key    = "input/chroma_db/"
}

resource "aws_s3_object" "output_folder" {
  bucket = aws_s3_bucket.rag_data.bucket
  key    = "output/chroma_db/"
}

resource "null_resource" "upload_dataset_to_s3" {
  provisioner "local-exec" {
    command = <<EOT
      aws s3 sync "${path.module}/../../../dataset" s3://${aws_s3_bucket.rag_data.bucket}/input/chroma_db --delete
    EOT
  }

  depends_on = [aws_s3_bucket.rag_data]
}

# Permissão para o S3 invocar a Lambda
resource "aws_lambda_permission" "allow_s3_invoke_embedding" {
  statement_id  = "AllowS3InvokeEmbedding"
  action        = "lambda:InvokeFunction"
  function_name = var.embedding_db_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.rag_data.arn
}

# Notificação S3 → Lambda
resource "aws_s3_bucket_notification" "trigger_embedding_lambda" {
  bucket = aws_s3_bucket.rag_data.id

  lambda_function {
    lambda_function_arn = var.embedding_db_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "input/chroma_db/"
    filter_suffix       = ".pdf"
  }

  depends_on = [
    aws_lambda_permission.allow_s3_invoke_embedding
  ]
}


