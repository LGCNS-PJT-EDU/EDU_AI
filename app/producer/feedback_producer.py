import json
import logging
import sys

from aiokafka import AIOKafkaProducer
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

producer: AIOKafkaProducer = None  # 전역으로 선언

async def init_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    await producer.start()

async def close_producer():
    global producer
    if producer:
        logger.info("Closing producer...")
        await producer.stop()
        producer = None

async def publish_success(payload) :
    logger.info("Publish success message")
    await producer.send_and_wait(TOPIC_RESULT_SUCCESS, value=payload)

async def publish_fail(original_payload, error_code: str, error_message: str) :
    payload = {
        **original_payload,
        "errorCode": error_code,
        "errorMessage": error_message,
    }
    logger.info("Publish fail message")
    await producer.send_and_wait(TOPIC_RESULT_FAIL, value=payload)