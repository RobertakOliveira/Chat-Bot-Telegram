## Recursos com tags + random suffixes, significa que os recursos criados terão sufixos aleatórios adicionados aos seus nomes.
# # Isso é importante para garantir que os recursos sejam únicos e evitar conflitos de nomes.

resource "random_id" "bucket_suffix" {
  byte_length = 4  # Sufixo randômico de 4 bytes 
}

resource "aws_s3_bucket" "docs" {
  bucket = "chatbot-docs-${random_id.bucket_suffix.hex}"  # Nome imprevisível do bucket S3 
  tags   = {
    Owner = var.owner_tag  # Rastreamento interno apenas 
  }
}