# 🤖 JusBot - Assistente Jurídico via Telegram

📋 Descrição
JusBot é um assistente jurídico inteligente que utiliza processamento de linguagem natural e recuperação de informações para analisar documentos jurídicos. Implementado como um bot do Telegram, o JusBot pode processar textos jurídicos, gerar embeddings semânticos e responder consultas jurídicas com base em uma base de conhecimento estruturada.

🌟 Funcionalidades

Processamento de Documentos Jurídicos: Extração automática de texto de PDFs
Geração de Embeddings: Transformação de textos jurídicos em representações vetoriais
Indexação Avançada: Armazenamento otimizado de embeddings para consulta rápida
Consulta Contextual: Responde perguntas com base nos documentos jurídicos indexados
Interface via Telegram: Acesso intuitivo através do aplicativo Telegram
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
jusbot/
├── assets/                # Recursos gráficos
├── dataset/               # Documentos jurídicos organizados por processo
│   
├── docker/                # Configurações de conteinerização
│   ├── docker-compose.yml # Configuração dos serviços
│   ├── dockerfile         # Instruções de build da imagem
│   └── entrypoint.sh      # Script de inicialização
├── src/                   # Código-fonte do projeto
│   ├── embeddings_generate/ # Geração de embeddings
│   │   └── Embbeding_Generator.py
│   ├── extractors/        # Extração de texto de documentos
│   │   ├── extrair_ocr.py
│   │   └── S3_Loader.py   # Gerenciamento de arquivos no S3
│   ├── Rag/               # Retrieval Augmented Generation
│   │   ├── chroma_conector.py
│   │   ├── chroma_generate/
│   │   ├── JusBot.py      # Núcleo do assistente
│   │   └── prompt_template.py
│   ├── telegram_bot/      # Interface do Telegram
│   │   ├── bot.py         # Configuração do bot
│   │   ├── handlers.py    # Manipuladores de comandos
│   │   └── rag_interface.py # Integração com o RAG
│   └── textos_extraidos/  # Textos processados
├── terraform/             # Infraestrutura como código
│   └── main.tf            # Definição de recursos AWS
├── .env                   # Variáveis de ambiente
└── requirements.txt       # Dependências Python
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

<div align="center">
🤖 JusBot - Tornando o conhecimento jurídico acessível através da inteligência artificial
</div>