#!/bin/bash

# ===================================================
# SCRIPT DE PROVISIONAMENTO PERSISTENTE PARA CHATBOT
# ===================================================

# Configurações
BASE_DIR="/opt/chatbot"
LOG_FILE="$BASE_DIR/logs/setup.log"
COMPOSE_FILE="$BASE_DIR/docker-compose.yml"
ENV_FILE="$BASE_DIR/.env"
CHROMA_DIR="$BASE_DIR/chroma_db"
LOG_DIR="$BASE_DIR/logs"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2" | tee -a "$LOG_FILE"
}

# 1. Criar estrutura de diretórios persistente
log "INFO" "Criando estrutura de diretórios em $BASE_DIR..."
mkdir -p "$BASE_DIR" "$CHROMA_DIR" "$LOG_DIR"
chmod -R 775 "$BASE_DIR"
chown -R $USER:$USER "$BASE_DIR"

# Verificar se diretórios foram criados
if [ ! -d "$BASE_DIR" ] || [ ! -d "$CHROMA_DIR" ] || [ ! -d "$LOG_DIR" ]; then
    log "ERRO" "Falha ao criar diretórios necessários!"
    exit 1
fi

# 2. Instalar Docker e Docker Compose
if ! command -v docker &> /dev/null; then
    log "INFO" "Instalando Docker..."
    apt-get update -y && apt-get install -y docker.io docker-compose
    systemctl enable --now docker
    usermod -aG docker $USER
    newgrp docker
fi

# 3. Criar arquivo .env
log "INFO" "Criando arquivo .env..."
cat > "$ENV_FILE" <<EOF
TELEGRAM_BOT_TOKEN=
API_SECRET_KEY=
USER_NAME=dev-
EOF

# Verificar se .env foi criado
if [ ! -f "$ENV_FILE" ]; then
    log "ERRO" "Falha ao criar o arquivo .env!"
    exit 1
else
    log "INFO" "Arquivo .env criado com sucesso:"
    cat "$ENV_FILE" | sed 's/^/  /' | tee -a "$LOG_FILE"
fi

# 4. Criar docker-compose.yml
log "INFO" "Criando docker-compose.yml..."
cat > "$COMPOSE_FILE" <<EOF
services:
  api:
    image: rhafaelyreis/bot-grupo-6:api-v1
    container_name: chatbot-api
    env_file: .env
    ports:
      - "8080:8080"
    volumes:
      - $CHROMA_DIR:/app/chroma_db
      - $LOG_DIR:/app/logs
    restart: unless-stopped
    networks:
      - chatbot-network

  bot:
    image: rhafaelyreis/bot-grupo-6:bot-v1
    container_name: telegram-bot
    env_file: .env
    environment:
      - API_URL=http://api:8080/ask
    volumes:
      - $LOG_DIR:/app/logs
    restart: unless-stopped
    depends_on:
      - api
    networks:
      - chatbot-network

networks:
  chatbot-network:
    driver: bridge
EOF

# 5. Baixar imagens
log "INFO" "Baixando imagens Docker..."
docker pull rhafaelyreis/bot-grupo-6:api-v1
docker pull rhafaelyreis/bot-grupo-6:bot-v1

# 6. Iniciar serviços
log "INFO" "Iniciando containers..."
cd "$BASE_DIR"
docker-compose up -d

# 7. Verificar status
sleep 5  # Aguardar inicialização
log "INFO" "Status dos containers:"
docker ps --filter "name=chatbot" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

log "✅ CONCLUÍDO! Sistema instalado em $BASE_DIR"
echo "• API: http://localhost:8080"
echo "• Bot: Verifique logs em $LOG_DIR"
echo "• Dados persistentes:"
echo "  - ChromaDB: $CHROMA_DIR"
echo "  - Logs: $LOG_DIR"