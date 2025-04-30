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

