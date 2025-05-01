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
 
# 2. Instalar AWS CLI (se não estiver instalado)
if ! command -v aws &> /dev/null; then
    log "INFO" "Instalando AWS CLI..."
    apt update -y
    apt install -y awscli
else
    log "INFO" "AWS CLI já está instalado."
fi
 
# 3. Verificar se arquivos existem
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
 
# 4. Criar diretórios adicionais (se necessário)
log "INFO" "Criando diretórios para dados persistentes..."
mkdir -p chroma_db logs
 
# 5. Build e execução
log "INFO" "Iniciando containers com Docker Compose..."
docker compose up --build -d
 
# 6. Verificar status
log "INFO" "Verificando containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
 
log "✅ CONCLUÍDO!"
echo "API: http://localhost:8080"
echo "Bot: Verifique logs com 'docker logs telegram-bot'"
