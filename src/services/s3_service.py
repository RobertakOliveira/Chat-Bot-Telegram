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
        logger.info(f"Inicializando S3Service para bucket: {bucket_name}")
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        logger.info(f"✅ S3Service inicializado com sucesso para bucket: {bucket_name}")
    
    def list_files(self):
        """
        Lista todos os arquivos no bucket S3
        
        Returns:
            list: Lista com os nomes dos arquivos no bucket
        """
        logger.info(f"Listando arquivos do bucket S3: {self.bucket_name}")
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            files = []
            
            logger.debug("Iniciando paginação de objetos S3")
            page_count = 0
            for page in paginator.paginate(Bucket=self.bucket_name):
                page_count += 1
                if 'Contents' in page:
                    page_files = [obj['Key'] for obj in page['Contents']]
                    files.extend(page_files)
                    logger.debug(f"Página {page_count}: {len(page_files)} arquivos encontrados")
                else:
                    logger.debug(f"Página {page_count}: Nenhum arquivo encontrado")

            logger.info(f"✅ Listados {len(files)} arquivos do S3 bucket: {self.bucket_name}")
            return files
        except Exception as e:
            logger.error(f"❌ Erro ao listar arquivos do S3: {str(e)}")
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
        logger.info(f"Baixando arquivo {object_key} do bucket {self.bucket_name}")
        # Garantir que o diretório de destino exista
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            logger.debug(f"Iniciando download: {object_key} -> {local_path}")
            self.s3_client.download_file(self.bucket_name, object_key, local_path)
            file_size = os.path.getsize(local_path)
            logger.info(f"✅ Arquivo {object_key} baixado com sucesso: {file_size/1024:.2f} KB")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao baixar arquivo {object_key}: {str(e)}")
            return False 