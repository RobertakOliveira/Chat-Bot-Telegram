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

<<<<<<< HEAD
# Copia o código da aplicação
=======
# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
>>>>>>> cf5489b22073993ac62db669d6f7107d9cd3be71
COPY . .

# Cria diretório do ChromaDB
RUN mkdir -p /app/data/chroma_db

<<<<<<< HEAD
# Variáveis de ambiente padrão
=======
# Define pasta app como raiz para garantir que o Python saiba onde procurar os pacotes/modules do seu projeto.
ENV PYTHONPATH=/app

# Define variáveis de ambiente padrão
>>>>>>> cf5489b22073993ac62db669d6f7107d9cd3be71
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
ENV AWS_REGION=us-east-1
ENV API_URL=http://api:8000/ask

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
