#!/bin/bash

# ==============================================
# SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# ==============================================
# Versão: 2.0
# Autor: Katcilane Souza
# ==============================================

# ----------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------
APP_DIR="/opt/chatbot"       
APP_USER="ubuntu"            
GIT_REPO="https://github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro"
LOG_FILE="/var/log/chatbot-setup.log"

# Função para registrar logs
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# ----------------------------
# 1. PREPARAÇÃO DO SISTEMA
# ----------------------------
log "Iniciando provisionamento da instância EC2"

# Atualiza pacotes
log "Atualizando pacotes do sistema..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y >> $LOG_FILE 2>&1
apt-get upgrade -y >> $LOG_FILE 2>&1

# Instala dependências essenciais
log "Instalando dependências básicas..."
apt-get install -y \
    python3-pip \
    python3-dev \
    libssl-dev \
    libffi-dev \
    nginx \
    git \
    libpq-dev \
    python3-venv \
    build-essential \
    unzip \
    wget >> $LOG_FILE 2>&1

# ----------------------------
# 2. CONFIGURAÇÃO DO PYTHON
# ----------------------------
log "Configurando ambiente Python..."
pip3 install --upgrade pip >> $LOG_FILE 2>&1
pip3 install virtualenv >> $LOG_FILE 2>&1

# ----------------------------
# 3. ESTRUTURA DE DIRETÓRIOS
# ----------------------------
log "Criando estrutura de diretórios..."
mkdir -p $APP_DIR/app
mkdir -p $APP_DIR/data/documents
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/scripts

# Ajusta permissões
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR

# ----------------------------
# 4. BAIXAR CÓDIGO-FONTE
# ----------------------------
log "Obtendo código-fonte do repositório..."
if [ ! -d "$APP_DIR/.git" ]; then
    git clone $GIT_REPO $APP_DIR >> $LOG_FILE 2>&1
else
    cd $APP_DIR && git pull >> $LOG_FILE 2>&1
fi

# ----------------------------
# 5. CONFIGURAR VIRTUALENV
# ----------------------------
log "Configurando ambiente virtual Python..."
python3 -m virtualenv $APP_DIR/venv >> $LOG_FILE 2>&1

# Instalar dependências Python
log "Instalando dependências Python..."
source $APP_DIR/venv/bin/activate && \
pip install --upgrade pip && \
pip install \
    langchain \
    chromadb \
    pypdf \
    sentence-transformers \
    flask \
    fastapi \
    uvicorn \
    python-dotenv \
    boto3 \
    awscli \
    python-multipart \
    transformers >> $LOG_FILE 2>&1
deactivate

# ----------------------------
# 6. CONFIGURAÇÕES DE AMBIENTE
# ----------------------------
log "Configurando variáveis de ambiente..."
cat <<EOF > $APP_DIR/.env
# Configurações da API
API_HOST=0.0.0.0
API_PORT=5000
API_SECRET_KEY=$(openssl rand -hex 32)

# Configurações do Telegram
TELEGRAM_BOT_TOKEN=""

# Configurações do ChromaDB
CHROMA_DB_PATH="$APP_DIR/data/chroma_db"
DOCUMENTS_DIR="$APP_DIR/data/documents"

# Configurações AWS
AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
EOF

# Proteger arquivo .env
chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

# ----------------------------
# 7. CONFIGURAR SERVIÇO SYSTEMD
# ----------------------------
log "Configurando serviço da API..."
cat <<EOF > /etc/systemd/system/chatbot-api.service
[Unit]
Description=Chatbot Juridico API
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR/app
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/uvicorn api:app --host 0.0.0.0 --port 5000
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=chatbot-api

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# 8. CONFIGURAR NGINX
# ----------------------------
log "Configurando Nginx como proxy reverso..."
cat <<EOF > /etc/nginx/sites-available/chatbot
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    access_log $APP_DIR/logs/nginx-access.log;
    error_log $APP_DIR/logs/nginx-error.log;
}
EOF

# Ativar configuração
ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default

# Testar e reiniciar Nginx
nginx -t >> $LOG_FILE 2>&1
systemctl restart nginx >> $LOG_FILE 2>&1

# ----------------------------
# 9. INICIAR SERVIÇOS
# ----------------------------
log "Iniciando serviços..."
systemctl daemon-reload
systemctl enable chatbot-api >> $LOG_FILE 2>&1
systemctl start chatbot-api >> $LOG_FILE 2>&1
systemctl enable nginx >> $LOG_FILE 2>&1
systemctl restart nginx >> $LOG_FILE 2>&1

# ----------------------------
# 10. FINALIZAÇÃO
# ----------------------------
log "Provisionamento concluído com sucesso!"
log "Informações de acesso:"
log " - API: http://localhost:5000"
log " - Nginx: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
log " - Logs da API: journalctl -u chatbot-api -f"
log " - Logs do Nginx: tail -f $APP_DIR/logs/nginx-*.log"

exit 0