import json
import logging
import sys
from datetime import datetime

from kafka import KafkaProducer

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS

TOPIC_RESULT_SUCCESS = "feedback.result.success"
TOPIC_RESULT_FAIL = "feedback.result.fail"

logger = logging.getLogger("feedback_producer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda m: json.dumps(m).encode("utf-8")
)

def publish_success(payload) :
    logger.info("Publish success message")
    producer.send(TOPIC_RESULT_SUCCESS, value=payload)
    producer.flush()

def publish_fail(original_payload, error_code: str, error_message: str) :
    failure_payload = {
        "userId": original_payload["userId"],
        "subjectId": original_payload["subjectId"],
        "type": original_payload["type"],
        "nth": original_payload["nth"],
        "errorCode": error_code,
        "errorMessage": error_message,
    }
    logger.info("Publish fail message")
    producer.send(TOPIC_RESULT_FAIL, value=failure_payload)
    producer.flush()