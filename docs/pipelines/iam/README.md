# Módulo IAM

Este módulo gerencia as permissões e papéis IAM necessários para o projeto.

## Recursos Criados

- **Papel IAM `lambda_exec_role`**: Papel de execução para as funções Lambda.
- **Políticas Gerenciadas**:
  - `AWSLambdaBasicExecutionRole`: Permite que a Lambda escreva logs no CloudWatch.
  - `AmazonS3FullAccess`: Concede acesso total ao S3.
  - `AmazonAPIGatewayAdministrator`: Permite integração com o API Gateway.
  - `AmazonBedrockFullAccess`: Concede acesso ao Amazon Bedrock.
  - `CloudWatchLogsFullAccess`: Permite acesso total ao CloudWatch Logs.

## Saídas

- `lambda_exec_role_arn`: ARN do papel IAM para execução das funções Lambda.

## Fluxo de Trabalho

1. **Criação do Papel**: O papel `lambda_exec_role` é criado com permissões específicas.
2. **Anexação de Políticas**: As políticas necessárias são anexadas ao papel.
3. **Integração**: O papel é utilizado pelas funções Lambda para acessar recursos como S3, API Gateway e CloudWatch.

Este módulo garante que as funções Lambda tenham as permissões necessárias para operar corretamente.
