#!/bin/bash

# ==============================================
# SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# ==============================================
# Objetivo: Automatiza a implantação da API e ambiente
#           para o projeto de Chatbot Jurídico
# Responsáveis: Time DevOps (Leon/Rafa/Talita)
# ==============================================

# ----------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------
APP_DIR="/opt/chatbot"       # Diretório principal da aplicação
APP_USER="ubuntu"            # Usuário que rodará o serviço
GIT_REPO="<URL_REPO>"        # Repositório Git do projeto
LOG_FILE="/var/log/chatbot-setup.log"  # Arquivo de log do provisionamento

# Função para registrar logs com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# ----------------------------
# 1. PREPARAÇÃO DO SISTEMA
# ----------------------------
log "Iniciando provisionamento da API do Chatbot Jurídico"

# Atualiza pacotes do sistema operacional
log "Atualizando pacotes..."
apt-get update -y >> $LOG_FILE 2>&1
apt-get upgrade -y >> $LOG_FILE 2>&1

# Instala dependências essenciais:
# - Python e bibliotecas de desenvolvimento
# - Nginx como proxy reverso
# - Git para controle de versão
log "Instalando dependências..."
apt-get install -y \
    python3-pip \
    python3-dev \
    libssl-dev \
    libffi-dev \
    nginx \
    git >> $LOG_FILE 2>&1

# ----------------------------
# 2. CONFIGURAÇÃO DO AMBIENTE PYTHON
# ----------------------------
log "Configurando ambiente Python..."
pip3 install --upgrade pip >> $LOG_FILE 2>&1
pip3 install virtualenv >> $LOG_FILE 2>&1

# ----------------------------
# 3. ESTRUTURA DE DIRETÓRIOS
# ----------------------------
log "Criando diretórios..."
mkdir -p $APP_DIR/app    # Código da aplicação
mkdir -p $APP_DIR/data   # Dados persistentes (ex: ChromaDB)
mkdir -p $APP_DIR/logs   # Logs da aplicação
chown -R $APP_USER:$APP_USER $APP_DIR  # Ajusta permissões

# ----------------------------
# 4. CÓDIGO-FONTE
# ----------------------------
# Clona ou atualiza o repositório Git
if [ ! -d "$APP_DIR/.git" ]; then
    log "Clonando repositório..."
    git clone $GIT_REPO $APP_DIR >> $LOG_FILE 2>&1
else
    log "Repositório já existe, atualizando..."
    cd $APP_DIR && git pull >> $LOG_FILE 2>&1
fi

# ----------------------------
# 5. AMBIENTE VIRTUAL PYTHON
# ----------------------------
log "Configurando virtualenv..."
python3 -m virtualenv $APP_DIR/venv >> $LOG_FILE 2>&1

# Instala dependências Python dentro do virtualenv
source $APP_DIR/venv/bin/activate && \
pip install -r $APP_DIR/app/requirements.txt >> $LOG_FILE 2>&1
deactivate

# ----------------------------
# 6. VARIÁVEIS DE AMBIENTE
# ----------------------------
log "Criando arquivo .env..."
cat <<EOF > $APP_DIR/.env
# Configurações gerais da API
API_SECRET_KEY=$(openssl rand -hex 24)  # Gera chave segura
API_PORT=5000

# Integração com Telegram (Leon)
TELEGRAM_BOT_TOKEN="SEU_TOKEN_AQUI"

# Configurações do ChromaDB (Rafa)
CHROMA_DB_PATH="$APP_DIR/data/chroma_db"
DOCUMENTS_DIR="$APP_DIR/data/documents"

# Configurações AWS (Talita)
AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
EOF

# Protege o arquivo .env
chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

# ----------------------------
# 7. SERVIÇO DA API (SYSTEMD)
# ----------------------------
log "Configurando serviço da API..."
cat <<EOF > /etc/systemd/system/chatbot-api.service
[Unit]
Description=Chatbot Juridico API
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR/app
EnvironmentFile=$APP_DIR/.env  # Carrega variáveis
ExecStart=$APP_DIR/venv/bin/uvicorn api:app --host 0.0.0.0 --port 5000
Restart=always  # Reinício automático em falhas

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# 8. NGINX (PROXY REVERSO)
# ----------------------------
log "Configurando Nginx..."
cat <<EOF > /etc/nginx/sites-available/chatbot
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;  # Encaminha para a API
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

# Ativa a configuração
ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled
nginx -t && systemctl restart nginx  # Valida e reinicia

# ----------------------------
# 9. INICIALIZAÇÃO DOS SERVIÇOS
# ----------------------------
log "Ativando serviços..."
systemctl daemon-reload
systemctl enable chatbot-api  # Habilita inicialização automática
systemctl start chatbot-api   # Inicia o serviço

# ----------------------------
# FINALIZAÇÃO
# ----------------------------
log "Provisionamento concluído com sucesso!"
log "Acesso:"
log " - API: http://localhost:5000"
log " - Nginx: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
log "Gerenciamento:"
log " - Ver logs: journalctl -u chatbot-api -f"
log " - Reiniciar: systemctl restart chatbot-api"

exit 0