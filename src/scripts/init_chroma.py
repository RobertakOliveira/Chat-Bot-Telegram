#!/usr/bin/env python
"""
Script de inicialização para carregar documentos no ChromaDB

Este script é executado durante a inicialização do contêiner Docker
para garantir que o ChromaDB esteja atualizado com os documentos do S3.
"""

import os
import sys
import logging
import argparse
import json
from dotenv import load_dotenv
import sys

sys.path.insert(0, './src/')
from config import Config
from services.s3_service import S3Service
from services.indexing.embedding_service import EmbeddingService
from services.indexing.document_loader_service import DocumentService
from repository.chromaDB_repo import ChromaRepository

import glob

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("init_chroma")

def load_chroma_db(filter_patterns=None, force_reload=False):
    """
    Carrega documentos do S3 no ChromaDB
    
    Args:
        filter_patterns: Lista de padrões para filtrar documentos
        force_reload: Se True, força o recarregamento de documentos já processados
        
    Returns:
        dict: Resultado do processamento
    """
    logger.info("=== Iniciando carregamento do ChromaDB ===")
    logger.info(f"Filtros: {filter_patterns}, Forçar recarregamento: {force_reload}")
    
    try:
        # Carrega variáveis de ambiente se não estiverem carregadas
        # load_dotenv(override=True)
        
        # Validação de configurações
        Config.validate()
        
        logger.info(f"Bucket S3: {Config.S3_BUCKET_NAME}")
        logger.info(f"ChromaDB Path: {Config.CHROMA_LOCAL_PATH}")
        
        # Criação dos clientes AWS
        s3_client, bedrock_client, _ = Config.get_aws_clients()
        
        # Inicialização dos serviços
        embedding_service = EmbeddingService(
            bedrock_client=bedrock_client,
            model_id=Config.EMBEDDING_MODEL_ID,
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        s3_service = S3Service(
            s3_client=s3_client,
            bucket_name=Config.S3_BUCKET_NAME
        )
        
        chroma_repository = ChromaRepository(
            embedding_function=embedding_service.get_embeddings(),
            collection_name=Config.CHROMA_COLLECTION,
            chroma_path=Config.CHROMA_LOCAL_PATH
        )
        
        document_service = DocumentService(
            s3_service=s3_service,
            embedding_service=embedding_service,
            chroma_repository=chroma_repository
        )
        
        # Processa os documentos
        if filter_patterns:
            # TODO: Implementar filtragem de documentos
            logger.info(f"Aplicando filtros: {filter_patterns}")
            # Por enquanto, ignora os filtros
        
        result = document_service.process_all_documents()
        
        success_result = {
            "status": "success",
            "message": "Carregamento do ChromaDB concluído com sucesso",
            "bucket": Config.S3_BUCKET_NAME,
            "collection": Config.CHROMA_COLLECTION,
            **result
        }
        
        logger.info("=== Resumo do Carregamento ===")
        logger.info(f"Status: {success_result['status']}")
        logger.info(f"Bucket: {success_result['bucket']}")
        logger.info(f"Arquivos processados: {len(success_result['processed_files'])}")
        logger.info(f"Arquivos com erro: {len(success_result['failed_files'])}")
        logger.info(f"Total de chunks: {success_result['total_chunks']}")
        
        return success_result
            
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "bucket": Config.S3_BUCKET_NAME if hasattr(Config, 'S3_BUCKET_NAME') else "não configurado"
        }
        
        logger.error(f"❌ Erro ao carregar o ChromaDB: {str(e)}", exc_info=True)
        logger.error(f"Status: {error_result['status']}")
        logger.error(f"Erro: {error_result['error']}")
        
        return error_result

def main():
    """
    Função principal chamada ao executar o script
    """
    parser = argparse.ArgumentParser(description='Inicializa e carrega o ChromaDB com documentos do S3')
    parser.add_argument('--filter', '-f', type=str, nargs='*', help='Lista de padrões para filtrar documentos')
    parser.add_argument('--force-reload', action='store_true', help='Força o recarregamento de documentos já processados')
    parser.add_argument('--output', '-o', type=str, help='Caminho para salvar o resultado em JSON')
    
    args = parser.parse_args()
    
    if len(glob.glob('../bd/*')) > 0:
        logger.info(' ✅ ChromaDB pré-carregado encontrado.')
        sys.exit(0)

    # Executa o carregamento
    result = load_chroma_db(
        filter_patterns=args.filter,
        force_reload=args.force_reload
    )
    
    # Salva o resultado em um arquivo se solicitado
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Resultado salvo em: {args.output}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultado em {args.output}: {str(e)}")
    
    # Retorna o código de saída com base no status
    sys.exit(0 if result["status"] == "success" else 1)

if __name__ == "__main__":
    main() 