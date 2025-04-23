FROM python:3.9-slim

WORKDIR /app

# Copia apenas os requirements primeiro para aproveitar cache
COPY requirements.txt .

ENV PYTHONPATH=/app

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Define o comando padrão (pode ser sobrescrito no compose)
CMD ["python", "--version"]