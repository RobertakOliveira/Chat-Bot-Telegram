#!/bin/bash

# ==============================================
# SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# Versão: 3.0
# Autor: Katcilane Souza
# ==============================================

# ----------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------

#!/bin/bash

# ==============================================
# SCRIPT DE PROVISIONAMENTO - CHATBOT JURÍDICO
# Versão: 3.1
# Autor: Katcilane Souza
# ==============================================

# ----------------------------
# CONFIGURAÇÕES GERAIS
# ----------------------------
APP_DIR="/opt/chatbot"
APP_USER="ubuntu"
REPO_URL="github.com/Compass-pb-aws-2025-JANEIRO/sprints-7-8-pb-aws-janeiro"
LOG_FILE="/var/log/chatbot-setup.log"
SCRIPTS_DIR="$APP_DIR/scripts"

# Carrega token do GitHub
if [ -f ".env_bootstrap" ]; then
    export $(grep -v '^#' .env_bootstrap | xargs)
fi

# Valida token
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "[ERRO] Variável GITHUB_TOKEN não definida. Crie o arquivo .env_bootstrap com: GITHUB_TOKEN=seu_token"
    exit 1
fi

# Define URL com autenticação
GIT_REPO="https://${GITHUB_TOKEN}@${REPO_URL}"




# ----------------------------
# FUNÇÃO DE LOG
# ----------------------------
log() {
    local level=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# ----------------------------
# FUNÇÃO PARA VERIFICAR ERROS
# ----------------------------
check_error() {
    local exit_code=$1
    local message=$2
    if [ $exit_code -ne 0 ]; then
        log "ERROR" "Falha: $message (Código: $exit_code)"
        exit $exit_code
    fi
}

# ----------------------------
# FUNÇÃO PARA EXECUTAR COMANDOS
# ----------------------------
run_cmd() {
    local cmd=$1
    local desc=$2
    log "INFO" "Executando: $desc"
    eval "$cmd" >> "$LOG_FILE" 2>&1
    check_error $? "$desc"
}

# ----------------------------
# 1. VERIFICAR CONEXÃO À INTERNET
# ----------------------------
log "INFO" "Verificando conexão com a internet..."

ping -c 4 google.com > /dev/null 2>&1
if [ $? -ne 0 ]; then
    log "ERROR" "Sem conexão com a internet! Verifique a configuração de rede."
    exit 1
else
    log "INFO" "Conexão com a internet estabelecida."
fi

# ----------------------------
# 2. VERIFICAR A URL DO REPOSITÓRIO
# ----------------------------
log "INFO" "Verificando URL do repositório..."

git ls-remote $GIT_REPO > /dev/null 2>&1
if [ $? -ne 0 ]; then
    log "ERROR" "Falha ao acessar o repositório. Verifique a URL ou permissões de acesso."
    exit 1
else
    log "INFO" "Repositório acessível com sucesso."
fi

# ----------------------------
# 3. VERIFICAÇÃO DE RECURSOS MÍNIMOS
# ----------------------------
MIN_MEMORY=1800 # 1.8GB
MIN_CPU=1       # 1 vCPU

TOTAL_MEM=$(free -m | awk '/Mem:/ {print $2}')
TOTAL_CPU=$(nproc)

if [ "$TOTAL_MEM" -lt "$MIN_MEMORY" ]; then
  log "ERROR" "Memória insuficiente! Mínimo recomendado: ${MIN_MEMORY}MB"
  exit 1
fi

if [ "$TOTAL_CPU" -lt "$MIN_CPU" ]; then
  log "ERROR" "CPUs insuficientes! Mínimo recomendado: ${MIN_CPU}vCPU"
  exit 1
fi

# ----------------------------
# 4. CRIAR DIRETÓRIO DE SCRIPTS
# ----------------------------
mkdir -p "$SCRIPTS_DIR"

# ----------------------------
# 5. PREPARAÇÃO DO SISTEMA
# ----------------------------
log "INFO" "Iniciando provisionamento da instância EC2"

run_cmd "apt-get update -y" "Atualizando pacotes do sistema"
run_cmd "apt-get upgrade -y" "Atualizando sistema"

# Instalar dependências essenciais
run_cmd "apt-get install -y python3-pip python3-dev libssl-dev libffi-dev nginx git libpq-dev python3-venv build-essential unzip wget" "Instalando dependências básicas"

# ----------------------------
# 6. CONFIGURAÇÃO DO PYTHON
# ----------------------------
run_cmd "pip3 install --upgrade pip" "Atualizando pip"
run_cmd "pip3 install virtualenv" "Instalando virtualenv"

# ----------------------------
# 7. ESTRUTURA DE DIRETÓRIOS
# ----------------------------
log "INFO" "Criando estrutura de diretórios..."
mkdir -p "$APP_DIR/app" || check_error $? "Criar diretório app"
mkdir -p "$APP_DIR/data/documents" || check_error $? "Criar diretório documents"
mkdir -p "$APP_DIR/logs" || check_error $? "Criar diretório logs"
mkdir -p "$SCRIPTS_DIR" || check_error $? "Criar diretório scripts"

# Ajusta permissões
run_cmd "chown -R $APP_USER:$APP_USER $APP_DIR" "Ajustando permissões"
run_cmd "chmod -R 755 $APP_DIR" "Ajustando permissões"

# ----------------------------
# 8. BAIXAR CÓDIGO-FONTE
# ----------------------------
if [ ! -d "$APP_DIR/.git" ]; then
    run_cmd "git clone $GIT_REPO $APP_DIR" "Clonando repositório"
else
    cd "$APP_DIR" && run_cmd "git pull" "Atualizando repositório"
fi

# ----------------------------
# 9. CONFIGURAR VIRTUALENV
# ----------------------------
run_cmd "python3 -m virtualenv $APP_DIR/venv" "Criando virtualenv"

# Instalar dependências Python
log "INFO" "Instalando dependências Python..."
source "$APP_DIR/venv/bin/activate" || check_error $? "Ativar virtualenv"

pip_packages=( \
    "langchain" \
    "chromadb" \
    "pypdf" \
    "sentence-transformers" \
    "flask" \
    "fastapi" \
    "uvicorn" \
    "python-dotenv" \
    "boto3" \
    "awscli" \
    "python-multipart" \
    "transformers" \
)

for package in "${pip_packages[@]}"; do
    run_cmd "pip install $package" "Instalando $package"
done

deactivate

# ----------------------------
# 10. CONFIGURAÇÕES DE AMBIENTE
# ----------------------------
log "INFO" "Configurando variáveis de ambiente..."
cat <<EOF > "$APP_DIR/.env" || check_error $? "Criar arquivo .env"
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
run_cmd "chown $APP_USER:$APP_USER $APP_DIR/.env" "Protegendo .env"
run_cmd "chmod 600 $APP_DIR/.env" "Protegendo .env"

# ----------------------------
# 11. CONFIGURAR SERVIÇO SYSTEMD
# ----------------------------
log "INFO" "Configurando serviço da API..."
cat <<EOF > "/etc/systemd/system/chatbot-api.service" || check_error $? "Criar serviço systemd"
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
# 12. CONFIGURAR NGINX
# ----------------------------
log "INFO" "Configurando Nginx como proxy reverso..."
cat <<EOF > "/etc/nginx/sites-available/chatbot" || check_error $? "Criar configuração Nginx"
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
run_cmd "ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled" "Ativar site Nginx"
run_cmd "rm -f /etc/nginx/sites-enabled/default" "Remover configuração padrão Nginx"

# Testar e reiniciar Nginx
run_cmd "nginx -t" "Testar configuração Nginx"
run_cmd "systemctl restart nginx" "Reiniciar Nginx"

# ----------------------------
# 13. INICIAR SERVIÇOS
# ----------------------------
log "INFO" "Iniciando serviços..."
run_cmd "systemctl daemon-reload" "Recarregar daemon systemd"
run_cmd "systemctl enable chatbot-api" "Habilitar serviço API"
run_cmd "systemctl start chatbot-api" "Iniciar serviço API"
run_cmd "systemctl enable nginx" "Habilitar Nginx"
run_cmd "systemctl restart nginx" "Reiniciar Nginx"

# ----------------------------
# 14. FINALIZAÇÃO
# ----------------------------
log "INFO" "Provisionamento concluído com sucesso!"
log "INFO" "Informações de acesso:"
log "INFO" " - API: http://localhost:5000"
log "INFO" " - Nginx: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
log "INFO" " - Logs da API: journalctl -u chatbot-api -f"
log "INFO" " - Logs do Nginx: tail -f $APP_DIR/logs/nginx-*.log"

# Configurar log rotation
echo "Configurando log rotation..."
cat <<EOF > /etc/logrotate.d/chatbot
${APP_DIR}/logs/*.log {
  daily
  missingok
  rotate 7
  compress
  delaycompress
  notifempty
  create 640 ubuntu ubuntu
  sharedscripts
}
EOF

exit 0
