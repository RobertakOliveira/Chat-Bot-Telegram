# Módulo API

Este módulo gerencia a configuração do API Gateway para expor as funções Lambda.

## Recursos Criados

- **API Gateway**: Configura a API para integrar com as funções Lambda.
- **Rotas**:
  - `POST /generateEmbeddings`: Rota para acionar a função `embedding_db`.
  - `POST /webhook`: Rota para acionar a função `telegram_rag`.
- **Integrações**:
  - `AWS_PROXY`: Integração direta com as funções Lambda.

## Variáveis

- `lambda_telegram_arn`: ARN da função Lambda `telegram_rag`.
- `lambda_telegram_name`: Nome da função Lambda `telegram_rag`.
- `embedding_db_arn`: ARN da função Lambda `embedding_db`.
- `embedding_db_name`: Nome da função Lambda `embedding_db`.

## Saídas

- `api_url`: URL pública da API Gateway.
- `execution_arn`: ARN usado para configurar permissões de invocação na Lambda.

## Fluxo de Trabalho

1. **Criação da API**: A API Gateway é configurada com rotas e integrações.
2. **Integração com Lambda**: As rotas acionam diretamente as funções Lambda.
3. **Exposição Pública**: A API é exposta publicamente para interação com o Telegram e processamento de embeddings.

Este módulo é responsável por expor as funcionalidades do projeto via API Gateway.
