# 🤖 JusBot - Assistente Jurídico via Telegram (Em Desenvolvimento)

> **Status do Projeto**: Em desenvolvimento ativo

JusBot é um assistente jurídico baseado em IA que responde a perguntas sobre documentos jurídicos através do Telegram. 
Utilizando tecnologias como Amazon Bedrock, ChromaDB e LangChain, o bot consulta documentos PDF para fornecer respostas.

## ✨ Características (Implementadas)

- **Consulta de documentos jurídicos**: Responde a perguntas baseadas apenas no conteúdo dos documentos disponíveis
- **Interface amigável via Telegram**: Menu intuitivo e interações personalizadas

## 🚧 Em Desenvolvimento

Este projeto está em fase de implementação, com as seguintes funcionalidades planejadas:


## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **Amazon Bedrock**: Para modelos de linguagem e embeddings
- **ChromaDB**: Para armazenamento e busca vetorial
- **LangChain**: Framework para aplicações de RAG (Retrieval Augmented Generation)
- **python-telegram-bot**: API para interação com o Telegram
- **AWS S3**: Para armazenamento de documentos (planejado)
- **AWS CloudWatch**: Para logs e monitoramento (planejado)

## 🔧 Requisitos

- Python 
- Conta AWS com acesso ao serviço Bedrock
- Bot do Telegram (token obtido via BotFather)
- Dependências listadas em `requirements.txt`

## 📦 Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/sprints-7-8-pb-aws-janeiro.git
cd sprints-7-8-pb-aws-janeiro
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

1. Crie um arquivo `.env` na raiz do projeto com:
```
# Token do Telegram (obtenha com @BotFather)
TELEGRAM_TOKEN=seu_token_aqui

# Configurações AWS
BUCKET_NAME=nome-do-seu-bucket
```

2. Configure suas credenciais AWS:
```bash
aws configure
```



## 🚀 Como Usar

1. Execute o bot:
```bash
python jusbot.py
```

2. No Telegram:
   - Abra uma conversa com seu bot
   - Envie "oi" ou uma "saudação" para receber o menu principal
   - Selecione "🔍 Consultar Documentos Jurídicos" para inicializar a base de conhecimento
   - Faça perguntas relacionadas aos documentos

## 📁 Estrutura do Projeto

```
sprints-7-8-pb-aws-janeiro/
├── assets/                  # Recursos do projeto
├── dataset/                 # Pasta para documentos jurídicos
├── .env                     # Arquivo de configuração 
├── jusbot.py                # Código principal do bot
├── Rag_Pipeline.py          # Implementação do pipeline RAG
├── README.md                # Esta documentação
├── requirements.txt         # Dependências do projeto
└── S3_Loader.py             # Módulo para carregamento de documentos do S3
```

## 📝 Arquivos Principais

- **jusbot.py**: Implementação do bot do Telegram com ChromaDB
- **Rag_Pipeline.py**: Pipeline de RAG (Retrieval Augmented Generation)
- **S3_Loader.py**: Funções para upload de documentos para S3

---

## 👥 Equipe

Leonardo de Freitas Nogueira 
Luis Herinque Trindade
Rafael Eich Fernandes
Simone de Oliveira Santos

---

**Nota**: Este projeto está em desenvolvimento ativo e algumas funcionalidades podem estar incompletas ou sujeitas a alterações.