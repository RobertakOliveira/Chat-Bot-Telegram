# chat/utils/logger.py
import logging
import time
from chat.utils.aws_clients import logs_client

LOG_GROUP = "/aws/chatbot-consultor-juridico"
_log_streams_created = set()


class CloudWatchHandler(logging.Handler):
    def __init__(self, client, group_name, stream_name):
        super().__init__()
        self.client = client
        self.group_name = group_name
        self.stream_name = stream_name
        self.sequence_token = None
        self._create_log_group_and_stream()

    def _create_log_group_and_stream(self):
        # Cria grupo se não existir
        try:
            logs_client.create_log_group(logGroupName=self.group_name)
        except logs_client.exceptions.ResourceAlreadyExistsException:
            pass

        # Cria o stream se não existir (só uma vez por execução)
        if self.stream_name not in _log_streams_created:
            try:
                logs_client.create_log_stream(
                    logGroupName=self.group_name,
                    logStreamName=self.stream_name
                )
                _log_streams_created.add(self.stream_name)
            except logs_client.exceptions.ResourceAlreadyExistsException:
                pass

    def emit(self, record):
        msg = self.format(record)
        timestamp = int(time.time() * 1000)
        log_event = {
            "logGroupName": self.group_name,
            "logStreamName": self.stream_name,
            "logEvents": [{"timestamp": timestamp, "message": msg}]
        }

        if self.sequence_token:
            log_event["sequenceToken"] = self.sequence_token

        try:
            response = self.client.put_log_events(**log_event)
            self.sequence_token = response["nextSequenceToken"]
        except self.client.exceptions.InvalidSequenceTokenException as e:
            self.sequence_token = e.response["expectedSequenceToken"]
            log_event["sequenceToken"] = self.sequence_token
            self.client.put_log_events(**log_event)


def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        cw_handler = CloudWatchHandler(logs_client, LOG_GROUP, module_name)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        cw_handler.setFormatter(formatter)
        logger.addHandler(cw_handler)

    return logger
