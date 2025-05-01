# Build telegram_RAG
resource "null_resource" "build_telegram_rag" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region ${var.aws_region} | \
        docker login --username AWS --password-stdin ${var.ecr_repo_url}

      docker buildx build --platform linux/amd64 \
        --build-arg LAMBDA_FILE=teste.py \
        --build-arg HANDLER_NAME=handler \
        -t telegram-rag -f ./Dockerfile .
      
      docker tag telegram-rag:latest ${var.ecr_repo_url}:telegram_rag
      docker push ${var.ecr_repo_url}:telegram_rag
    EOT
  }
  triggers = {
    always_run = timestamp()
  }
}

resource "aws_lambda_function" "telegram_rag" {
  function_name = "telegram_RAG"
  role          = var.exec_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:telegram_rag"
  memory_size   = 128
  timeout       = 30
  depends_on    = [null_resource.build_telegram_rag]
}

data "archive_file" "embedding_db_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../application"
  output_path = "${path.module}/../embedding_db_payload.zip"
}

resource "aws_lambda_function" "embedding_db" {
  function_name = "embedding_db"
  role          = var.exec_role_arn
  handler       = "gerar_embeddings.handler"
  runtime       = "python3.10"
  memory_size   = 512
  timeout       = 300

  filename         = data.archive_file.embedding_db_zip.output_path
  source_code_hash = data.archive_file.embedding_db_zip.output_base64sha256

  environment {
    variables = {
      INPUT_BUCKET  = var.bucket_name
      INPUT_PREFIX  = "input/chroma_db/"
      OUTPUT_BUCKET = var.bucket_name
      OUTPUT_PREFIX = "output/chroma_db/"
    }
  }
}
