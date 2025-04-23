#!/bin/bash

# ==============================================
# SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# Versão Dockerizada
# ==============================================

# Configurações
APP_DIR="/opt/chatbot"
LOG_FILE="/var/log/chatbot-setup.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2" | tee -a "$LOG_FILE"
}

# 1. Instalar Docker
log "INFO" "Instalando Docker..."
apt-get update -y
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io

# 2. Instalar Docker Compose
log "INFO" "Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Criar estrutura de diretórios
log "INFO" "Criando estrutura de diretórios..."
mkdir -p "$APP_DIR/data/chroma_db"
mkdir -p "$APP_DIR/logs"

# 4. Clonar repositório (se necessário)
if [ ! -d "$APP_DIR/.git" ]; then
    log "INFO" "Clonando repositório..."
    git clone https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro.git "$APP_DIR"
fi

# 5. Configurar .env
log "INFO" "Configurando variáveis de ambiente..."
cat <<EOF > "$APP_DIR/.env"
# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=$(openssl rand -hex 32)

# Configurações do Telegram
TELEGRAM_BOT_TOKEN=""

# Configurações AWS
AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)

# Configurações ChromaDB
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
EOF

# 6. Iniciar serviços com Docker Compose
log "INFO" "Iniciando serviços com Docker Compose..."
cd "$APP_DIR/docker" && docker-compose up -d

log "INFO" "Provisionamento concluído com sucesso!"