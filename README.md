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
