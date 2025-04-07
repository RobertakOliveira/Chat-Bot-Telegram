# Backend com encryption ativada, significa que os dados armazenados no backend serão criptografados e protegidos.
# Isso é importante para garantir a segurança dos dados sensíveis armazenados no backend.

terraform {
  backend "s3" {      # Configuração do backend S3 para o Terraform
    # O backend S3 é usado para armazenar o estado do Terraform em um bucket S3.
    # Isso permite que várias pessoas colaborem no mesmo projeto, mantendo o estado sincronizado. 
    # O bucket S3 deve ser criado previamente e o nome do bucket deve ser único na conta AWS.
    bucket         = "chatbot-tfstate-${var.owner_tag}"  # Nome do bucket S3 onde o estado do Terraform será armazenado.
    key            = "terraform.tfstate" # Caminho dentro do bucket S3 onde o estado do Terraform será armazenado.
    region         = var.aws_region       # Região AWS onde o bucket S3 está localizado.
    encrypt        = true                 # Ativa a criptografia para o estado do Terraform armazenado no S3.
    dynamodb_table = "terraform-locks"     # Nome da tabela DynamoDB usada para bloquear o estado do Terraform.
  }
}