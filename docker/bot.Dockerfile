# Stage 1: Builder
FROM python:3.9-slim as builder
 
WORKDIR /app
 
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
 
# Stage 2: Final
FROM python:3.9-slim
 
WORKDIR /app
 
COPY --from=builder /root/.local /root/.local
COPY . .
 
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH
ENV API_URL=http://api:8000/ask
 
CMD ["python", "app/bot.py"]