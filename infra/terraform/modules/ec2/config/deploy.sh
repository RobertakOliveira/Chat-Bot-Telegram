#!/bin/bash

# Atualizar sistema
sudo yum update -y

# Instalar Python, AWS CLI e dependências do sistema
sudo yum install -y python3 python3-pip python3-devel gcc
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Criar diretório da aplicação
sudo mkdir -p /opt/chatbot
sudo chown -R ec2-user:ec2-user /opt/chatbot

# Configurar ambiente virtual
cd /opt/chatbot
python3 -m venv venv
source venv/bin/activate

# Tentar copiar arquivos do S3 (com retry)
max_retries=5
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    echo "Tentativa $((retry_count + 1)) de copiar arquivos do S3..."
    aws s3 cp s3://${S3_BUCKET_NAME}/app/ /opt/chatbot/ --recursive && \
    aws s3 cp s3://${S3_BUCKET_NAME}/config/requirements.txt /opt/chatbot/ && \
    aws s3 cp s3://${S3_BUCKET_NAME}/config/deploy.sh /opt/chatbot/scripts/ && break
    retry_count=$((retry_count + 1))
    sleep 10
done

if [ $retry_count -eq $max_retries ]; then
    echo "Falha ao copiar arquivos do S3 após $max_retries tentativas"
    exit 1
fi

# Instalar dependências Python
pip install --upgrade pip
pip install -r /opt/chatbot/requirements.txt

# Configurar variáveis de ambiente
cat << EOF > /opt/chatbot/.env
AWS_DEFAULT_REGION=us-east-1
CHROMA_DB_PATH=/opt/chatbot/chroma_db
LOG_LEVEL=INFO
EOF

# Configurar serviço da API
cat << EOF > /etc/systemd/system/chatbot.service
[Unit]
Description=Chatbot Service
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/chatbot
Environment="PATH=/opt/chatbot/venv/bin"
Environment="S3_BUCKET_NAME=${S3_BUCKET_NAME}"
ExecStart=/opt/chatbot/venv/bin/python -m uvicorn app.api.chatbackend:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar serviço do bot do Telegram
cat << EOF > /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Bot Service
After=network.target chatbot.service

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/chatbot
Environment="PATH=/opt/chatbot/venv/bin"
Environment="TELEGRAM_TOKEN=${TELEGRAM_TOKEN}"
ExecStart=/opt/chatbot/venv/bin/python -m app.bots.botTelegram
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar logs
sudo mkdir -p /var/log/chatbot
sudo touch /var/log/chatbot/chatbot.log
sudo chown -R ec2-user:ec2-user /var/log/chatbot

# Configurar CloudWatch Agent
sudo yum install -y amazon-cloudwatch-agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
sudo systemctl start amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent

# Iniciar serviços
sudo systemctl daemon-reload
sudo systemctl enable chatbot
sudo systemctl enable telegram-bot
sudo systemctl start chatbot
sudo systemctl start telegram-bot

# Verificar status
sudo systemctl status chatbot
sudo systemctl status telegram-bot 