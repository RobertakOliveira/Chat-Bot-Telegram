# Módulo S3

Este módulo gerencia o bucket S3 e os recursos relacionados para o projeto.

## Recursos Criados

- **S3 Bucket**: Armazena os dados de entrada e saída para embeddings.
- **S3 Object**: Cria as pastas `input/chroma_db/` e `output/chroma_db/` no bucket.
- **Lambda Permission**: Concede permissão ao S3 para invocar a função Lambda `embedding_db`.
- **Bucket Notification**: Configura notificações para acionar a Lambda `embedding_db` quando novos objetos são criados no bucket.

## Variáveis

- `embedding_db_arn`: ARN da função Lambda `embedding_db`.
- `embedding_db_name`: Nome da função Lambda `embedding_db`.

## Saídas

- `bucket_name`: Nome do bucket S3 criado.

## Fluxo de Trabalho

1. **Entrada de Dados**: Arquivos PDF são enviados para a pasta `input/chroma_db/` no bucket.
2. **Notificação**: A criação de novos objetos na pasta de entrada aciona a função Lambda `embedding_db`.
3. **Processamento**: A Lambda processa os dados e armazena os resultados na pasta `output/chroma_db/`.

Este módulo é essencial para o fluxo de dados do projeto, garantindo a integração entre o S3 e a Lambda.
