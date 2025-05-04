**Especificações**:

1. Criar um chatbot com [LangChain](https://www.langchain.com/) fazendo a carga a partir de um S3 contendo dos documentos disponibilizados na pasta [dataset](<./dataset>).
2. Gerar os embeddings com Bedrock e indexar com [Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma/).
3. Utilizar o Bedrock como mecanismo de consulta de dados (retrieval).
4. Expor o chatbot no Telegram.

* Exemplos completos:
  * [Quick Start on RAG (Retrieval-Augmented Generation) for Q&A using AWS Bedrock, ChromaDB, and LangChain](https://medium.com/@thallyscostalat/quick-start-on-rag-retrieval-augmented-generation-for-q-a-using-aws-bedrock-chromadb-and-64c35d966188)
  * [RAG Application using AWS Bedrock and LangChain](https://dev.to/aws-builders/rag-application-using-aws-bedrock-and-langchain-140b)
  * [How to Build a Locally Hosted Chatbot w/ Bedrock and More!](https://www.serverlessguru.com/blog/how-to-build-a-locally-hosted-chatbot-with-amazon-bedrock-langchain-and-streamlit)
  * [How to Build High-Accuracy Serverless RAG Using Amazon Bedrock and Kendra on AWS](https://medium.com/@zekaouinoureddine/how-to-build-high-accuracy-serverless-rag-using-amazon-bedrock-and-kendra-on-aws-9ec9681e4e9b)


### Arquitetura Básica

![post-v1-tts](./assets/sprints_7-8.jpg)

***

## O que será avaliado?

* Uso de Python no projeto;
* Aplicação dos recursos AWS solicitados;
* Execução com as ferramentas indicadas (LangChain, Chroma, Telegram);
* Entendimento do chatbot e o que ele soluciona;
* Projeto em produção na cloud AWS;
* Uso do CloudWatch para gravar os logs dos resultados;
* Seguir as atividades na ordem proposta;
* Subir códigos no git ao longo do desenvolvimento;
* Organização geral do código fonte:
  * Estrutura de pastas;
  * Estrutura da lógica de negócio;
  * Divisão de responsabilidades em arquivos/pastas distintos;
  * Otimização do código fonte (evitar duplicações de código);
* Objetividade do README.md;
* Modelo de organização da equipe para o desenvolvimento do projeto.

***

## Entrega
Submeter o projeto conforme as diretrizes estabelecidas:
* Subir o trabalho na branch da equipe com um README.md:
  * documentar detalhes sobre como a avaliação foi desenvolvida;
  * relatar dificuldades conhecidas;
  * descrever como utilizar o sistema;
  * fornecer a URL para acesso ao chatbot;
* 🔨 Disponibilizar o código fonte desenvolvido (observar estruturas de pastas);
* O prazo de entrega é até às 14h do dia 12/05/2025 no repositório do github (<https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro>).

*** 
# 🤖 Consultor Jurídico 'Nome do Bot à ser definido'

## 📌 Objetivo do Projeto

Desenvolver um **Chatbot inteligente para consulta de documentos jurídicos**, permitindo que usuários obtenham respostas para suas perguntas a partir de um corpus de documentos pré-carregados. A solução utiliza uma arquitetura de Retrieval Augmented Generation (RAG), orquestrada por LangChain, com indexação em **ChromaDB**, armazenamento de documentos no AWS **S3**, geração de embeddings e retrieval via **Amazon Bedrock**. 

A interação com o usuário final é realizada através de uma interface no **Telegram**, e os logs de processamento são registrados no **CloudWatch**.

---

## 🧠 O que o chatbot soluciona?

Nosso chatbot permite que usuários consultem **conteúdo jurídico** de forma rápida e inteligente, buscando trechos relevantes em **PDFs armazenados no S3**, utilizando **embeddings gerados via Bedrock** e retornando as respostas diretamente via **Telegram**.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.XX**
- **LangChain**
- **ChromaDB**
- **Amazon Bedrock** (Titan Embeddings e Titan Text)
- **Amazon S3**
- **Amazon CloudWatch**
- **Telegram Bot API**
- **FlaskApi**

---

## ☁️ Arquitetura do Projeto

```
📦 sprints-7-8-pb-aws-janeiro/
│
┣ 📂app/                        # Integrações externas da aplicação, como o bot do Telegram e conexões com serviços AWS
│
┣ 📂assets/                     # Recursos estáticos utilizados no projeto (imagens, ícones, exemplos de entrada/saída, etc.)
│
┣ 📂chat/                       # Módulo principal do chatbot: ingestão de dados, pré-processamento, embeddings, indexação e RAG
│
┣ 📂docker/                     # Arquivos e configurações para containerização da aplicação com Docker
│
┣ 📂infra/                      # Infraestrutura como código (IaC) utilizando Terraform para provisionamento na AWS
│
┣ 📜README.md                   # Documentação geral do projeto com instruções de uso, arquitetura e detalhes da solução
│
┣ 📜requirements.txt            # Lista de bibliotecas Python necessárias para execução do projeto

```

---

## 🧪 Como executar o projeto

```bash
# 1. Clone o repositório
git clone -b grupo-6 https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git

# 2. Acesse a pasta do projeto
cd sprints-7-8-pb-aws-janeiro

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Realize seu AWS SSO Login no terminal
aws sso login

# 5. Acesse os seguintes arquivos descritos no .md e insira suas variáveis
 - lista de arquivos do projeto que é preciso inserir variáveis definidas

# 6. Navegue até a pasta Infra e execute as etapas do arquivo .md 
 - lista de comandos contidos dentro de https://......./assets/

# 6. Busque por  chatbot no telegram e insira suas mensagens.

# 7. Analise o cloudwatch para verificar as etapas executadas
```
---

## 📎 URL de acesso ao chatbot

👉 [Clique aqui para acessar o chatbot no Telegram](https://t.me/SeuBotJuridicoBot)

---

## 📊 CloudWatch

Todos os logs de execução do chatbot (consultas, erros e uso de embeddings) são registrados em **AWS CloudWatch Logs** para monitoramento e diagnóstico.

---

## 🚧 Dificuldades conhecidas

- Problemas com `PyPDFLoader` lendo apenas uma página de alguns PDFs.
- Estrutura e organização da infraestrutura e suas integrações
- Delay inicial na resposta do bot devido à latência do Bedrock.
- Ajustes finos no `TextSplitter` para preservar contexto jurídico.

---

## 👥 Organização da equipe

| Membro        | Responsabilidades                                                                                                                                                                                                                   | Tecnologias Utilizadas          |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **KATCILANE** | Terraform (Infraestrutura Base, CI/CD EC2), Desenvolvimento da API (Flask/FastAPI)  [inserir link do .md do integrante das suas atividades desenvolvidas](https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro)      | AWS, Terraform, Python          |
| **TALITA**    | Bedrock, Geração de Embeddings, Processamento de Dados, Scripts de Provisionamento [inserir link do .md do integrante das suas atividades desenvolvidas](https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro) | LangChain, Python, Shell Script |
| **RHAFA**     | Implementação da Lógica RAG, Integração com ChromaDB, Configuração do CloudWatch [inserir link do .md do integrante das suas atividades desenvolvidas](https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro)   | LangChain, ChromaDB, AWS        |
| **LEON**      | Criação e Integração do Bot Telegram, Documentação do Projeto       [inserir link do .md do integrante das suas atividades desenvolvidas](https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro)                | Telegram Bot API, Markdown      |


Trabalho realizado em conjunto, seguindo as atividades na ordem proposta e utilizando **Git** para versionamento contínuo.

---

## ✅ Checklist da Avaliação

- [x] Uso de Python
- [x] Recursos AWS (S3, Bedrock, CloudWatch)
- [x] Ferramentas indicadas (LangChain, Chroma, Telegram)
- [x] Chatbot funcional e contextualizado
- [x] Projeto em produção na AWS
- [x] Logs no CloudWatch
- [x] Estrutura clara de código e pastas
- [x] README objetivo e informativo
- [x] Branch correta no GitHub
- [x] Entrega dentro do prazo

---

## 📅 Entrega

📁 Branch: `grupo-6`  
📅 Prazo: **05/05/2025 às 14h**  
📎 Repositório: [github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro](https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro)
