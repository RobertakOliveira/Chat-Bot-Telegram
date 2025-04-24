# Etapa 1: Builder
FROM python:3.9-slim AS builder
 
WORKDIR /app
 
# Instala ferramentas para compilar dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .
 
# Instala dependências no diretório /install para não poluir a imagem final
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt
 
# Etapa 2: Final (imagem leve)
FROM python:3.9-slim
 
WORKDIR /app
 
# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app \
    CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db \
    AWS_REGION=us-east-1 \
    API_URL=http://api:8000/ask
 
# Copia as dependências já instaladas no diretório /install do builder
COPY --from=builder /install /usr/local
 
# Copia todo o código do projeto para o container
COPY . .
 
# Cria diretório para o ChromaDB
RUN mkdir -p /app/data/chroma_db
 
EXPOSE 8000
 
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
