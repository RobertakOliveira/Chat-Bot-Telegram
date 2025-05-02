#!/bin/bash

SCRIPTS_DIR="/app/src"
LOCK_FILE="/app/.initialized"

SCRIPTS=(
    "extractors/S3_Loader.py"
    "extractors/extrair_ocr.py"
    "embeddings_generate/Embbeding_Generator.py"
    "Rag/chroma_generate/index_chroma.py"
)

if [ ! -f "$LOCK_FILE" ]; then
    echo "Executando scripts de inicialização..."
    for script in "${SCRIPTS[@]}"; do
        echo "Rodando: $script"
        python "$SCRIPTS_DIR/$script" || { echo "Erro em $script"; exit 1; }
    done
    touch "$LOCK_FILE"
fi

echo "Iniciando o bot Telegram..."
exec python "$SCRIPTS_DIR/telegram_bot/bot.py"