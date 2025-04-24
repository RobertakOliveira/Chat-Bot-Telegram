import os
import logging

logger = logging.getLogger("s3_service")

class S3Service:
    def __init__(self, s3_client, bucket_name):
        """
        Inicializa o serviço S3
        
        Args:
            s3_client: Cliente boto3 para S3
            bucket_name: Nome do bucket S3
        """
        self.s3_client = s3_client
        self.bucket_name = bucket_name
    
    def list_files(self):
        """
        Lista todos os arquivos no bucket S3
        
        Returns:
            list: Lista com os nomes dos arquivos no bucket
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            files = []

            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    files.extend([obj['Key'] for obj in page['Contents']])

            logger.info(f"Listados {len(files)} arquivos do S3 bucket: {self.bucket_name}")
            return files
        except Exception as e:
            logger.error(f"Erro ao listar arquivos do S3: {str(e)}")
            return []
    
    def download_file(self, object_key, local_path):
        """
        Baixa um arquivo do S3 para o caminho local
        
        Args:
            object_key: Chave do objeto no S3
            local_path: Caminho local para salvar o arquivo
        
        Returns:
            bool: True se o download foi bem-sucedido, False caso contrário
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_key, local_path)
            logger.debug(f"Arquivo {object_key} baixado para {local_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao baixar arquivo {object_key}: {str(e)}")
            return False 