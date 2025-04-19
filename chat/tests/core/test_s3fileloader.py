from langchain_community.document_loaders import S3FileLoader, PyPDFLoader
from chat.utils.aws_clients import s3_client


def simple_load_test(bucket: str, key: str):
    try:
        loader = S3FileLoader(
            bucket=bucket,
            key=key,
            loader_cls=PyPDFLoader,
            s3_client=s3_client
        )
        raw_docs = loader.load()
        print(
            f"Carregamento bem-sucedido. Número de documentos: {len(raw_docs)}")
    except Exception as e:
        print(f"Erro durante o carregamento: {e}")


if __name__ == "__main__":
    bucket = "consultor-juridico"  # Substitua pelo seu bucket
    key = "juridicos/78-agravo.pdf"  # Substitua pela sua chave
    simple_load_test(bucket, key)

# Navegue até a pasta raiz e execute:
#     python -m chat.tests.core.test_s3fileloader
