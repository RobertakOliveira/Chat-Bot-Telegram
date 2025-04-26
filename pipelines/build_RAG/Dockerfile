FROM lukewiwa/aws-lambda-python-sqlite:3.10

# Define o diretório correto da pasta lambda_RAG relativa ao Dockerfile
COPY application/ ${LAMBDA_TASK_ROOT}/

# Copia o requirements.txt e instala as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Define o handler da função Lambda
CMD ["teste.handler"]
