# Telegram RAG
resource "null_resource" "build_telegram_rag" {
  provisioner "local-exec" {
    command = <<EOT
      docker buildx build --platform linux/amd64 \
        -t telegram-rag -f ./Dockerfile.telegram_RAG .
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

# Embedding DB
resource "null_resource" "build_embedding_db" {
  provisioner "local-exec" {
    command = <<EOT
      docker buildx build --platform linux/amd64 \
        -t embedding-db -f ./Dockerfile.Embeddings_db .
      docker tag embedding-db:latest ${var.ecr_repo_url}:embedding_db
      docker push ${var.ecr_repo_url}:embedding_db
    EOT
  }

  triggers = {
    always_run = timestamp()
  }
}

resource "aws_lambda_function" "embedding_db" {
  function_name = "embedding_db"
  role          = var.exec_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repo_url}:embedding_db"
  memory_size   = 512
  timeout       = 300

  environment {
    variables = {
      INPUT_BUCKET  = var.bucket_name
      INPUT_PREFIX  = "input/chroma_db/"
      OUTPUT_BUCKET = var.bucket_name
      OUTPUT_PREFIX = "output/chroma_db/"
      BOT_TOKEN = var.bot_token
    }
  }

  depends_on = [null_resource.build_embedding_db]
}
