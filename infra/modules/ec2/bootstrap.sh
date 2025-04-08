
# O código abaixo é um script Bash projetado para automatizar a configuração e execução da aplicação de chatbot jurídico em um servidor Linux.
# Em resumo, este script automatiza os seguintes passos:
# 1. Atualiza a lista de pacotes do sistema.
# 2. Instala as dependências básicas: Python 3, pip e Git.
# 3. Clona o código do chatbot jurídico do GitHub para o diretório /opt/chatbot.
# 4. Instala todas as bibliotecas Python necessárias listadas no arquivo requirements.txt do projeto.
# 5. Cria um serviço systemd para gerenciar a execução da API do chatbot. Este serviço garante que a aplicação seja iniciada corretamente, reiniciada em caso de falha e executada sob um usuário específico.
# 6. Habilita o serviço para que ele seja iniciado automaticamente na inicialização do sistema.
# 7. Inicia o serviço chatbot imediatamente após a configuração.

# Para usar este script, é necessário:
# - Substituir https://github.com/seu-repo/chatbot-juridico.git pelo URL correto do repositório.
# - Verificar se o caminho para o arquivo principal da API (/opt/chatbot/app/api.py) está correto.
# - Verificar se o nome do usuário (ubuntu) é o usuário correto no servidor.
# - Garantir que exista um arquivo requirements.txt na raiz do repositório com todas as dependências Python.


#!/bin/bash
# Instala dependências básicas
apt-get update -y
apt-get install -y python3-pip git

# Clona o repositório (substitua pelo seu)
git clone https://github.com/seu-repo/chatbot-juridico.git /opt/chatbot

# Instala requirements
pip3 install -r /opt/chatbot/requirements.txt

# Configura serviço systemd
cat <<EOF > /etc/systemd/system/chatbot.service
[Unit]
Description=Chatbot Juridico Service

[Service]
ExecStart=/usr/bin/python3 /opt/chatbot/app/api.py
WorkingDirectory=/opt/chatbot/app
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

systemctl enable chatbot
systemctl start chatbot