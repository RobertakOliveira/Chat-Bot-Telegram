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

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etapa 2: Final (imagem leve)
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    PYTHONPATH=/app

# Copia as dependências já instaladas no diretório /install do builder
COPY --from=builder /install /usr/local

# Copia o código da aplicação
COPY . .

# Cria diretório do ChromaDB
RUN mkdir -p /app/data/chroma_db

# Variáveis de ambiente padrão
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
ENV AWS_REGION=us-east-1

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
