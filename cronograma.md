# Projeto: Chatbot Jurídico com Terraform e AWS

## 📋 Visão Geral
Chatbot para consulta de documentos jurídicos utilizando:
- **AWS Bedrock** (modelos de IA)
- **LangChain + ChromaDB** (RAG)
- **Telegram** (interface)
- **Terraform** (infra como código)
- **CloudWatch** (monitoramento)

## 📅 Cronograma (03/04 - 12/05/2025)

### 🛠️ Semana 1 (03/04 - 09/04): Infraestrutura
| Tarefa | Responsável | Entregáveis |
|--------|------------|-------------|
| Módulos Terraform (S3, IAM) | Membro 1 | `infra/modules/s3` |
| Configurar Bedrock | Membro 2 | Políticas IAM |
| CloudWatch via TF | Membro 3 | Dashboards |
| Setup Git | Membro 4 | Branch `grupo-1` |

### 📊 Semana 2 (10/04 - 16/04): Dados
| Tarefa | Responsável | Entregáveis |
|--------|------------|-------------|
| Extrair textos (PyPDF) | Membro 2 | `app/data_processing.py` |
| Gerar embeddings | Membro 3 | Lambda function |
| Indexar ChromaDB | Membro 1 | Vector store |

### 🔗 Semana 3 (17/04 - 23/04): Integração
| Tarefa | Responsável | Entregáveis |
|--------|------------|-------------|
| Implementar RAG | Membro 3 | `app/rag_chain.py` |
| API Gateway | Membro 1 | TF module |

### 🤖 Semana 4 (24/04 - 30/04): Telegram
| Tarefa | Responsável | Entregáveis |
|--------|------------|-------------|
| Criar bot | Membro 4 | Webhook |
| Integrar Lambda | Membro 1 | Handler |

### ✨ Semana 5 (01/05 - 07/05): Finalização
| Tarefa | Responsável | Entregáveis |
|--------|------------|-------------|
| Otimizar custos | Membro 2 | Relatório |
| Documentação | Membro 4 | README.md |

## 👥 Divisão de Tarefas
| Membro | Responsabilidades | Tecnologias |
|--------|-------------------|-------------|
| 1 KATCILANE | Terraform (S3, Lambda) | AWS, Python |
| 2 TALITA | Bedrock + Embeddings | LangChain |
| 3 RAFA | RAG + ChromaDB | Vector DBs |
| 4 LEON| Telegram + Docs | Bot API |

## 🏗️ Estrutura de Arquivos
```bash
.
├── infra/               # Código Terraform
│   ├── main.tf          # Config principal
│   └── modules/         # Módulos reutilizáveis
├── app/                 # Código Python
│   ├── rag_chain.py     # Lógica RAG
│   └── telegram_bot.py  # Handler do bot
└── README.md            # Documentação