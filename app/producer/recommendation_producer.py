import json
import logging
import sys

from aiokafka import AIOKafkaProducer

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS

RECOM_RESULT_SUCCESS_TOPIC = "recom.result.success"
RECOM_RESULT_FAIL_TOPIC = "recom.result.fail"

logger = logging.getLogger("recommendation_producer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

producer: AIOKafkaProducer = None

async def init_recommendation_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retry_backoff_ms=1000,
        request_timeout_ms=30000,
        acks="all",
        enable_idempotence=True
    )
    await producer.start()

async def close_recommendation_producer():
    global producer
    if producer:
        logger.info("Closing producer...")
        await producer.stop()
        producer = None

async def publish_recommendation_success(payload):
    try:
        logger.info("Try to publish success message...")
        await producer.send_and_wait(RECOM_RESULT_SUCCESS_TOPIC, value=payload)
        logger.info("Publish success message")
    except Exception as e:
        logger.error(f"Failed to send success message: {e}")
        payload = {
            "userId": payload["userId"],
            "subjectId": payload["subjectId"],
        }
        await publish_recommendation_fail(payload, error_code="FEEDBACK_SUCCESS_PUBLISH_FAIL_ERROR",
                                    error_message="Failed to publish success message")


async def publish_recommendation_fail(original_payload, error_code: str, error_message: str):
    payload = {
        **original_payload,
        "errorCode": error_code,
        "errorMessage": error_message,
    }
    logger.info("Try to publish failed message...")
    await producer.send_and_wait(RECOM_RESULT_FAIL_TOPIC, value=payload)
    logger.info("Publish fail message")
