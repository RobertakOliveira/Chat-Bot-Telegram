FROM lukewiwa/aws-lambda-python-sqlite:3.10

COPY application/ ${LAMBDA_TASK_ROOT}/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG LAMBDA_FILE=teste.py
ARG HANDLER_NAME=handler

CMD ["teste.handler"]
