# Stage 1: Builder
FROM python:3.9-slim as builder
 
WORKDIR /app
 
# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
 
# Stage 2: Final
FROM python:3.9-slim
 
WORKDIR /app
 
# Copia somente o necessário do builder
COPY --from=builder /root/.local /root/.local
 
# Copia o código-fonte
COPY . .
 
# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
ENV AWS_REGION=us-east-1
 
RUN mkdir -p /app/data/chroma_db
 
EXPOSE 8000
 
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]