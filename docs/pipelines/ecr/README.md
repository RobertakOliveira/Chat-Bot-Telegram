# Módulo ECR

Este módulo gerencia o repositório ECR utilizado para armazenar as imagens Docker das funções Lambda.

## Recursos Criados

- **Repositório ECR `lambda-docker-repo`**: Repositório para armazenar as imagens Docker.

## Variáveis

- `force_delete`: Define se o repositório deve ser excluído forçadamente ao destruir o recurso.

## Saídas

- `repository_url`: URL do repositório ECR criado.

## Fluxo de Trabalho

1. **Criação do Repositório**: O repositório ECR é criado para armazenar imagens Docker.
2. **Upload de Imagens**: As imagens Docker das funções Lambda são enviadas para o repositório.
3. **Integração com Lambda**: As funções Lambda utilizam as imagens armazenadas no ECR.

Este módulo é essencial para o deploy das funções Lambda baseadas em imagens Docker.
