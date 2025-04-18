FROM public.ecr.aws/lambda/python:3.8

# Define o diretório correto da pasta lambda_RAG relativa ao Dockerfile
COPY lambda_RAG/ ${LAMBDA_TASK_ROOT}/

# Copia o requirements.txt e instala as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Define o handler da função Lambda
CMD ["lambda_rag.handler"]
