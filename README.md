# Chatbot para Consulta de Documentos Jurídicos

## 🎯 Objetivo

Criar um sistema de RAG (Retrieval Augmented Generation) usando AWS Bedrock para consulta de documentos jurídicos através de um chatbot no Telegram, com armazenamento em S3, banco de embeddings Chroma, e logs no CloudWatch.

## 🏗️ Arquitetura

![Arquitetura do Projeto](./assets/sprints_7-8.jpg)

O projeto implementa a seguinte arquitetura:
- **S3**: Armazenamento dos documentos jurídicos
- **EC2**: Hospedagem da aplicação
- **Bedrock**: Geração de embeddings e consulta ao modelo de linguagem
- **LangChain**: Framework para processamento de linguagem natural e construção do RAG
- **Chroma**: Banco de vetores para armazenamento de embeddings
- **Telegram**: Interface do chatbot
- **CloudWatch**: Monitoramento e logs da aplicação

## 🔧 Tecnologias Utilizadas

- **AWS**:
  - S3 para armazenamento de documentos
  - EC2 para hospedagem da aplicação
  - Bedrock para embeddings e LLM
  - CloudWatch para logs
  - API Gateway para exposição da API
  - IAM para gerenciamento de permissões
- **Python**:
  - LangChain para construção do RAG
  - Chroma para banco de vetores
  - PyPDF para processamento de PDFs
  - python-telegram-bot para interface com Telegram
- **IaC**:
  - Terraform para provisionar infraestrutura

## 📝 Componentes do Projeto

### Infraestrutura (Terraform)

- **VPC**: Configuração da rede virtual
- **S3**: Bucket para armazenamento dos documentos jurídicos
- **EC2**: Instância para executar a aplicação
- **CloudWatch**: Configuração de logs
- **API Gateway**: Exposição da API
- **IAM**: Roles e permissões

### Aplicação

- **embeddings.py**: Geração e armazenamento de embeddings usando Bedrock e Chroma
- **chatbackend.py**: Backend do chatbot com LangChain e RAG
- **botTelegram.py**: Interface do chatbot no Telegram


## <div align="center">Sobre os Autores
### **Eduardo Augusto De Oliveira Mendes**  
🌐 [GitHub](https://github.com/EduAugustoM) | [LinkedIn](https://www.linkedin.com/in/eduardo-augusto-mendes/) 

### **Emanuelle Meireles**
🌐 [GitHub](https://github.com/EmanuelleMeireles) | [LinkedIn](https://www.linkedin.com/in/emanuelle-meireles-a4b331317/)

### **Osvaldo Gomes de Oliveira Neto**
🌐 [GitHub](https://github.com/Osvaldo-arq) | [LinkedIn](https://www.linkedin.com/in/osvaldo-gomes-de-oliveira-neto-026306269/)
