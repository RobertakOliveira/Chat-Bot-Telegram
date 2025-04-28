#! bin/bash

python3 src/scripts/init_chroma.py

gunicorn --workers=2 --chdir=/src/ main:app -b unix:/shared/chatbotsocket.sock