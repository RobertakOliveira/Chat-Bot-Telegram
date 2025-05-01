#!/bin/bash
 
# ===================================================
# SCRIPT DE PROVISIONAMENTO PARA CHATBOT DOCKERIZADO
# - Usa arquivos existentes (Dockerfiles, requirements.txt, etc.)
# - API FastAPI + Telegram Bot + ChromaDB
# - Rede isolada entre containers
# ===================================================
 
# Configurações
LOG_FILE="/var/log/chatbot-setup.log"
 
# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2" | tee -a "$LOG_FILE"
}
 
# 1. Instalar Docker e Docker Compose (se não existirem)
if ! command -v docker &> /dev/null; then
    log "INFO" "Instalando Docker..."
    apt update -y
    apt install -y docker.io docker-compose
    systemctl enable docker
    systemctl start docker
    usermod -aG docker $USER
    newgrp docker
else
    log "INFO" "Docker já está instalado."
fi
 
# 2. Verificar se arquivos existem
log "INFO" "Verificando arquivos do projeto..."
REQUIRED_FILES=(
    "docker/Dockerfile.api"
    "docker/Dockerfile.bot"
    "requirements.txt"
    "docker-compose.yml"
    ".env"
)
 
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log "ERRO" "Arquivo não encontrado: $file"
        exit 1
    fi
done
 
# 3. Criar diretórios adicionais (se necessário)
log "INFO" "Criando diretórios para dados persistentes..."
mkdir -p chroma_db logs
 
# 4. Build e execução
log "INFO" "Iniciando containers com Docker Compose..."
docker compose up --build -d
 
# 5. Verificar status
log "INFO" "Verificando containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
 
log "✅ CONCLUÍDO!"
echo "API: http://localhost:8080"
echo "Bot: Verifique logs com 'docker logs telegram-bot'"
 
# #!/bin/bash
 
# # ==============================================
# # SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# # Versão Dockerizada
# # ==============================================
 
# # Configurações
# APP_DIR="/opt/chatbot/docker"
# LOG_FILE="/var/log/chatbot-setup.log"
 
# # Função de log
# log() {
#     echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2" | tee -a "$LOG_FILE"
# }
 
# # 1. Remover Docker antigo (se existir)
# log "INFO" "Removendo versões antigas do Docker..."
# apt remove --purge -y docker.io containerd || true
# apt autoremove -y
 
# # 2. Instalar Docker oficial
# log "INFO" "Instalando Docker oficial..."
# apt update -y
# apt install -y ca-certificates curl gnupg lsb-release
 
# install -m 0755 -d /etc/apt/keyrings
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
# chmod a+r /etc/apt/keyrings/docker.gpg
 
# echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
#   https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
#   tee /etc/apt/sources.list.d/docker.list > /dev/null
 
# apt update -y
# apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
 
# log "INFO" "Ativando Docker..."
# usermod -aG docker $USER
# newgrp docker
# systemctl enable docker
# systemctl start docker
 
# # 3. Criar estrutura de diretórios
# log "INFO" "Criando estrutura do projeto em $APP_DIR..."
# mkdir -p "$APP_DIR/data/chroma_db"
# mkdir -p "$APP_DIR/logs"
# cd "$APP_DIR"
 
# # 4. Gerar arquivos do projeto
# log "INFO" "Gerando arquivos padrão..."
 
# # Dockerfile
# cat <<EOF > Dockerfile
# FROM python:3.9-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# EOF
 
# # requirements.txt
# cat <<EOF > requirements.txt
# uvicorn
# fastapi
# EOF
 
# # docker-compose.yml
# cat <<EOF > docker-compose.yml
# version: '3.8'
# services:
#   app:
#     build: .
#     ports:
#       - "8000:8000"
#     restart: unless-stopped
# EOF
 
# # main.py
# cat <<EOF > main.py
# from fastapi import FastAPI
 
# app = FastAPI()
 
# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}
# EOF
 
# # 5. Criar arquivo .env
# log "INFO" "Configurando variáveis de ambiente..."
# cat <<EOF > "$APP_DIR/.env"
# API_HOST=0.0.0.0
# API_PORT=8000
# API_SECRET_KEY=$(openssl rand -hex 32)
# TELEGRAM_BOT_TOKEN=""
# AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
# CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
# EOF
 
# # 6. Subir com Docker Compose
# log "INFO" "Subindo aplicação com Docker Compose..."
# docker-compose up -d --build
 
# log "✅ PROVISIONAMENTO CONCLUÍDO!"
# echo "Acesse via: http://<SEU_IP>:8000"
 