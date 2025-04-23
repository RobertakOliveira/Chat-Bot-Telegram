# 🤖 Projeto: Chatbot Jurídico Inteligente com Terraform e AWS

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)](https://github.com/SEU_USUARIO/SEU_REPOSITORIO)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-blue)](https://opensource.org/licenses/MIT)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-%237B42F4.svg?style=for-the-badge&logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-%23008080.svg?style=for-the-badge&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-%234B0082.svg?style=for-the-badge&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![CloudWatch](https://img.shields.io/badge/CloudWatch-%23FF9900.svg?style=for-the-badge&logo=amazon-cloudwatch&logoColor=white)

## 💡 Visão Geral

Este projeto visa desenvolver um chatbot jurídico inteligente capaz de consultar documentos legais utilizando tecnologias de ponta na nuvem AWS. A arquitetura do chatbot combina a capacidade de modelos de linguagem da **AWS Bedrock** com a técnica de **Retrieval-Augmented Generation (RAG)**, implementada com **LangChain** e **ChromaDB**, para fornecer respostas contextuais e relevantes. A interação com o usuário será facilitada através do **Telegram**, e toda a infraestrutura será provisionada e gerenciada como código utilizando **Terraform**. O **AWS CloudWatch** garantirá o monitoramento e a observabilidade da aplicação.

## 🗓️ Cronograma Detalhado (03/04/2025 - 12/05/2025)

| Semana | Período       | Foco Principal        | Tarefas Principais                                                                  | Responsáveis | Entregáveis                                                                                                                               |
|--------|---------------|-----------------------|-------------------------------------------------------------------------------------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **1** | 03/04 - 09/04 | **Infraestrutura Base** | - Criação de módulos Terraform para S3, IAM, VPC e Security Group.                  | Membro 1     | `infra/modules/s3`, `infra/modules/vpc`, `infra/modules/security_group`, `infra/modules/iam`                                            |
|        |               |                       | - Configuração das políticas de acesso IAM para o serviço AWS Bedrock.                | Membro 2     | Políticas IAM para Bedrock                                                                                                                  |
|        |               |                       | - Provisionamento de dashboards e alarmes básicos no AWS CloudWatch via Terraform.     | Membro 3     | Dashboards, Alarms (básico)                                                                                                                 |
|        |               |                       | - Configuração inicial do repositório Git e criação da branch `grupo-1`.              | Membro 4     | Branch `grupo-1` no repositório Git                                                                                                         |
| **2** | 10/04 - 16/04 | **EC2 e Dependências** | - Criação do módulo Terraform para provisionar a instância EC2.                      | Membro 1     | `infra/modules/ec2`                                                                                                                       |
|        |               |                       | - Configuração do acesso SSH seguro à instância EC2.                                  | Membro 1     | Chave SSH configurada na EC2                                                                                                                |
|        |               |                       | - Elaboração e execução de script de provisionamento para instalar Python, LangChain e ChromaDB na EC2. | Membro 2     | Script de provisionamento (`bootstrap.sh`)                                                                                              |
| **3** | 17/04 - 23/04 | **Dados e Indexação** | - Implementação de script Python para extrair texto de documentos jurídicos (PyPDF) na EC2. | Membro 2     | `app/data_processing.py` (executável na EC2)                                                                                             |
|        |               |                       | - Desenvolvimento de script Python para gerar embeddings dos documentos (executável na EC2). | Membro 2     | Script para geração de embeddings (executável na EC2)                                                                                      |
|        |               |                       | - Indexação dos embeddings no banco de vetores ChromaDB hospedado na EC2.             | Membro 3     | Banco de vetores ChromaDB populado na EC2                                                                                                     |
| **4** | 24/04 - 30/04 | **Integração e API** | - Implementação da lógica de Retrieval-Augmented Generation (RAG) na EC2.           | Membro 3     | `app/rag_chain.py` (integrado com ChromaDB na EC2)                                                                                          |
|        |               |                       | - Desenvolvimento de uma API (Flask ou FastAPI) para receber requisições do Telegram na EC2. | Membro 1     | `app/api.py` (rodando na EC2)                                                                                                               |
|        |               |                       | - Configuração da regra no Security Group da EC2 para permitir acesso à porta da API. | Membro 1     | Regra de firewall configurada no Security Group da EC2                                                                                      |
| **5** | 01/05 - 07/05 | **Telegram e Finalização** | - Criação e configuração do bot no Telegram.                                       | Membro 4     | Token do bot Telegram                                                                                                                       |
|        |               |                       | - Implementação do webhook no Telegram para enviar mensagens para a API na EC2.        | Membro 4     | `app/telegram_bot.py` (envia requisições para a API na EC2)                                                                                  |
|        |               |                       | - Integração completa do bot Telegram com a API rodando na EC2.                       | Membro 1     | Comunicação bidirecional funcionando entre o Telegram e a API do chatbot                                                                    |
| **6** | 08/05 - 12/05 | **Otimização e Docs** | - Análise e implementação de estratégias para otimizar os custos da instância EC2.  | Membro 2     | Relatório de custos da EC2 e recomendações de otimização                                                                                      |
|        |               |                       | - Configuração avançada do CloudWatch para monitoramento detalhado da EC2 e logs da aplicação. | Membro 3     | Configuração avançada do CloudWatch (Logs, Métricas da EC2)                                                                                 |
|        |               |                       | - Elaboração e finalização da documentação completa do projeto no `README.md`.         | Membro 4     | `README.md` detalhado com arquitetura, configuração e instruções de uso                                                                     |

## 🧑‍🤝‍🧑 Divisão de Tarefas e Responsabilidades

| Membro       | Responsabilidades                                                                   | Tecnologias Utilizadas          |
|--------------|-------------------------------------------------------------------------------------|-------------------------------|
| **KATCILANE** | Terraform (Infraestrutura Base, EC2), Desenvolvimento da API (Flask/FastAPI)         | AWS, Terraform, Python        |
| **TALITA** | Bedrock, Geração de Embeddings, Processamento de Dados, Scripts de Provisionamento | LangChain, Python, Shell Script |
| **RAFA** | Implementação da Lógica RAG, Integração com ChromaDB, Configuração do CloudWatch     | LangChain, ChromaDB, AWS      |
| **LEON** | Criação e Integração do Bot Telegram, Documentação do Projeto                      | Telegram Bot API, Markdown    |

## 📂 Estrutura de Arquivos do Projeto//


```bash
.
├── infra/                  # Configuração Terraform
│   ├── backend.tf          # Estado remoto (S3)
│   ├── providers.tf        # Configuração de providers
│   ├── variables.tf        # Variáveis globais
│   ├── terraform.tfvars    # Valores locais (não versionado)
│   │
│   └── modules/           # Módulos reutilizáveis
│       ├── ec2/           # Configuração de instâncias EC2
│       │   ├── main.tf    # Definição da instância
│       │   ├── iam.tf     # Permissões IAM
│       │   └── cloudwatch.tf # Alarmes e métricas
│       │
│       └── s3/            # Configuração de buckets
│           ├── main.tf    # Bucket e versionamento
│           ├── encryption.tf # Criptografia AES256
│           └── policies.tf # Acesso IAM
│
├── app/                   # Código-fonte
│   ├── api.py             # API Flask/FastAPI
│   ├── rag_chain.py       # Integração RAG (LangChain)
│   └── telegram_bot.py    # Handler do bot
│
├── docs/                  # Documentação
│   ├── architecture.md    # Diagrama de arquitetura
│   └── setup-guide.md     # Guia de implantação
│
└── scripts/               # Automação
    └── bootstrap.sh       # Script de provisionamento
```
**Descrição dos diretórios e arquivos:**

* **`infra/`**: Contém todo o código Terraform necessário para provisionar e gerenciar a infraestrutura na AWS.
    * **`main.tf`**: Arquivo principal de configuração do Terraform, onde os recursos são definidos.
    * **`modules/`**: Diretório que armazena módulos Terraform reutilizáveis para diferentes componentes da infraestrutura.
        * **`s3/`**: Módulo para criar e configurar buckets S3.
        * **`iam/`**: Módulo para definir políticas e roles do IAM.
        * **`vpc/`**: Módulo para configurar a rede virtual privada (VPC) na AWS.
        * **`security_group/`**: Módulo para definir as regras de firewall para a EC2.
        * **`ec2/`**: Módulo para provisionar e configurar a instância EC2.
* **`app/`**: Contém o código Python da aplicação do chatbot.
    * **`rag_chain.py`**: Implementa a lógica principal do Retrieval-Augmented Generation, orquestrando a busca vetorial e a geração de respostas.
    * **`telegram_bot.py`**: Lida com a comunicação com a API do Telegram, recebendo mensagens dos usuários e enviando respostas.
    * **`api.py`**: Define a API (usando Flask ou FastAPI) que recebe as requisições do `telegram_bot.py`.
    * **`data_processing.py`**: Contém scripts para extrair o texto relevante dos documentos jurídicos (por exemplo, usando a biblioteca PyPDF).
    * **`embeddings.py`**: Inclui scripts para gerar os embeddings (representações vetoriais) dos documentos, utilizando LangChain e um modelo de embedding.
* **`scripts/`**: Armazena scripts auxiliares, como scripts de provisionamento para configurar a instância EC2 (`bootstrap.sh`).
* **`README.md`**: Este arquivo, que fornece uma visão geral do projeto, instruções de configuração e outras informações relevantes.