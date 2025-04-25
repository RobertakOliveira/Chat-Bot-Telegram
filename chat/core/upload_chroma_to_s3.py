# chat/scripts/upload_chroma_to_s3.py

import boto3
import os
from chat.utils.config import config

def upload_chroma_to_s3(file_name):
    """Faz o upload do arquivo Chroma compactado para o bucket S3"""
    s3_client = boto3.client('s3')
    bucket_name = config.S3_BUCKET_CHROMADB  # Assumindo que você configurou o nome do bucket no arquivo config

    try:
        print(f"🚀 Enviando {file_name} para o S3...")
        s3_client.upload_file(file_name, bucket_name, file_name)  # Faz o upload para o bucket configurado
        print(f"✅ Arquivo {file_name} enviado para o bucket S3 '{bucket_name}' com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar {file_name} para o S3: {e}")
        raise
