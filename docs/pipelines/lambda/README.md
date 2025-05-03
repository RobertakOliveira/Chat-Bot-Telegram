# Módulo Lambda

Este módulo gerencia as funções Lambda utilizadas no projeto.

## Recursos Criados

- **Função Lambda `embedding_db`**: Processa os dados de entrada do S3 e gera embeddings.
- **Função Lambda `telegram_rag`**: Integra o bot do Telegram com o fluxo de consulta jurídica.

## Variáveis

- `lambda_file`: Caminho para o arquivo Python da Lambda.
- `handler_name`: Nome do handler da função Lambda.
- `tag`: Tag para identificar a imagem Docker da Lambda.
- `ecr_repo_url`: URL do repositório ECR para imagens Docker.
- `exec_role_arn`: ARN do papel IAM para execução da Lambda.
- `bucket_name`: Nome do bucket S3 utilizado.

## Saídas

- `embedding_db_arn`: ARN da função Lambda `embedding_db`.
- `embedding_db_name`: Nome da função Lambda `embedding_db`.
- `lambda_telegram_arn`: ARN da função Lambda `telegram_rag`.
- `lambda_telegram_name`: Nome da função Lambda `telegram_rag`.

## Fluxo de Trabalho

1. **Deploy**: As funções Lambda são criadas a partir de imagens Docker armazenadas no ECR.
2. **Integração com S3**: A função `embedding_db` é acionada por eventos do S3.
3. **Integração com API Gateway**: A função `telegram_rag` é exposta via API Gateway para interagir com o Telegram.

Este módulo é responsável por toda a lógica de processamento e integração do projeto.
