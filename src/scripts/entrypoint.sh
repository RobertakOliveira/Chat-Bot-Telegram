#!/bin/bash

# Executar o script de inicialização e aguardar sua conclusão
python3 /src/scripts/init_chroma.py && \
# Somente após a conclusão bem-sucedida, iniciar o gunicorn
gunicorn --workers=2 --chdir=/src/ main:app -b unix:/shared/chatbotsocket.sock