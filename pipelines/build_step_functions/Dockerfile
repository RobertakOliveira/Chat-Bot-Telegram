FROM public.ecr.aws/lambda/python:3.8

ARG LAMBDA_FILE
ARG HANDLER_NAME

COPY application/${LAMBDA_FILE} ${LAMBDA_TASK_ROOT}/main.py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["main.handler"]

