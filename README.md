# Avaliação das Sprints 7 e 8 - Programa de Bolsas Compass UOL / AWS - turma janeiro/2025

Avaliação das sétima e oitava sprints do programa de bolsas Compass UOL para formação em Inteligência Artificial para AWS.

# 🌐 Integração API Gateway + Lambda + Telegram Bot (Webhook)

Este documento descreve o processo de criação e configuração da comunicação entre o bot do Telegram e a função AWS Lambda via API Gateway utilizando Webhook.

---

## 🎯 Objetivo

Permitir que mensagens enviadas ao bot no Telegram sejam recebidas automaticamente por uma função AWS Lambda através de uma rota HTTP (Webhook) gerenciada pelo API Gateway.

---

## ✅ Etapas realizadas

### 1. Criação do Bot no Telegram
- Foi utilizado o **@BotFather** para criar o bot.
- Comando: `/newbot`
- O bot gerado recebeu um **TOKEN**, que foi salvo para uso posterior como variável de ambiente na Lambda (`TELEGRAM_TOKEN`).

---

### 2. Criação da função Lambda
- Linguagem: **Python 3.11**
- A função `chatbotTelegramHandler` foi definida para receber requisições HTTP.
- Foram atribuídas permissões de acesso a S3, Bedrock, CloudWatch (via IAM Role).
- Foram configuradas as seguintes variáveis de ambiente na Lambda:
  - `TELEGRAM_TOKEN`
  - `BUCKET_NAME`
  - `REGION`
  - `CHROMA_DIR`
  - `S3_PREFIX`

---

### 3. Configuração da API Gateway (HTTP API)

#### a) Criação da API:
- Tipo: **HTTP API**
- Nome: `chatbotTelegramAPI`

#### b) Criação da rota:
- Caminho: `/telegram`
- Método: `POST`

#### c) Integração com Lambda:
- A rota `/telegram` foi conectada à função Lambda.
- A opção **"Add permissions for API Gateway to invoke Lambda"** foi confirmada automaticamente.

#### d) Deploy da API:
- Foi criado o **stage "prod"**.
- O deploy foi feito manualmente após a criação da rota.

#### e) Resultado:
- URL final do endpoint:
  ```
  https://4pr7evvg14.execute-api.us-east-1.amazonaws.com/prod/telegram
  ```

---

### 4. Registro do Webhook no Telegram
- Comando HTTP utilizado:

```
https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://4pr7evvg14.execute-api.us-east-1.amazonaws.com/prod/telegram
```

- Foi feita uma chamada de teste com `curl` para confirmar:
```bash
curl -X POST https://4pr7evvg14.execute-api.us-east-1.amazonaws.com/prod/telegram \
     -H "Content-Type: application/json" \
     -d '{"mensagem": "teste"}'
```

---

### 5. Verificação dos Logs
- Os logs da execução da Lambda foram verificados no **AWS CloudWatch**.
- O grupo de logs `/aws/lambda/chatbotTelegramHandler` foi criado automaticamente.
- As mensagens recebidas via Webhook foram logadas com sucesso.

---

## 🧠 Observações importantes

- Certifique-se de que o **método da rota seja POST.**
- Sempre realize o **deploy do stage** após qualquer alteração.
---