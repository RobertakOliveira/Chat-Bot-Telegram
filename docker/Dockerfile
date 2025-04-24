# Este Dockerfile configura um ambiente leve baseado na imagem oficial do Python 3.9-slim.
# Ele é projetado para executar uma aplicação Python utilizando o framework FastAPI.

# 1. Define o diretório de trabalho como /app.
# 2. Instala dependências do sistema necessárias para compilar pacotes Python.
# 3. Copia o arquivo requirements.txt para o container para instalar as dependências Python.
# 4. Define a variável de ambiente PYTHONPATH para garantir que o diretório /app seja reconhecido como raiz do projeto.
# 5. Instala as dependências Python listadas no arquivo requirements.txt.
# 6. Copia todo o código do projeto para o container.
# 7. Cria um diretório específico para persistência de dados do ChromaDB.
# 8. Define variáveis de ambiente padrão para o diretório de persistência do ChromaDB e a região AWS.
# 9. Expõe a porta 8000, que será usada pela API.
# 10. Define o comando padrão para iniciar o servidor FastAPI utilizando o Uvicorn.

FROM python:3.9-slim

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os requirements primeiro para aproveitar cache
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Cria diretório para o ChromaDB
RUN mkdir -p /app/data/chroma_db

# Define pasta app como raiz para garantir que o Python saiba onde procurar os pacotes/modules do seu projeto.
ENV PYTHONPATH=/app

# Define variáveis de ambiente padrão
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
ENV AWS_REGION=us-east-1
ENV API_URL=http://api:8000/ask

# Porta padrão para a API
EXPOSE 8000

# Comando padrão (pode ser sobrescrito no compose)
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]