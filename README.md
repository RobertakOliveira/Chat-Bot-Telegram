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
python main.py
```

2. No Telegram:
   - Abra uma conversa com seu bot
   - Envie "oi" ou uma "saudação" para receber o menu principal
   - Faça perguntas relacionadas aos documentos

## 📁 Estrutura do Projeto

```
sprints-7-8-pb-aws-janeiro/
│
├── main.py                  # Ponto de entrada da aplicação, interface Telegram
│
├── README.md                # Documentação do projeto
├── requirements.txt         # Dependências do projeto
├── .env                     # Arquivo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo git
│
├── telegram_bot/            # Módulo de processamento do bot
│   ├── __init__.py          # Torna o diretório um pacote Python
│   └── telegram_bot.py      # Lógica principal de processamento
│
├── Rag_Pipeline.py          # Pipeline de RAG (Retrieval Augmented Generation)
├── S3_Loader.py             # Carregar documentos do S3 da AWS
│
├── assets/                  #  Recursos do projeto
│
└── dataset/                 # Pasta para documentos jurídicos
```

## 📝 Arquivos Principais

- **main.py**: Ponto de entrada da aplicação. Contém a lógica de interação com o usuário via Telegram, incluindo comandos e mensagens.

- **telegram_bot/telegram_bot.py**:Módulo com as funções principais do bot, como processamento das mensagens, consultas jurídicas, saudação e envio de logs para o CloudWatch.

- **Rag_Pipeline.py**:Implementa a pipeline RAG (Retrieval-Augmented Generation), que usa embeddings e busca vetorial para consultar documentos jurídicos de forma inteligente.

- **S3_Loader.py**:Responsável por interagir com o AWS S3: envia e carrega documentos jurídicos que serão usados para gerar a base de conhecimento do bot.
---

## 👥 Equipe

- 👨‍💻 Leonardo de Freitas Nogueira 
- 👨‍💻 Luis Henrique Trindade 
- 👨‍💻 Rafael Eich Fernandes 
- 👩‍💻 Simone de Oliveira Santos 


---

**Nota**: Este projeto está em desenvolvimento ativo e algumas funcionalidades podem estar incompletas ou sujeitas a alterações.