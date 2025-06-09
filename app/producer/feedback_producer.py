import json
import logging
import sys

from aiokafka import AIOKafkaProducer

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS

FEEDBACK_RESULT_SUCCESS_TOPIC = "feedback.result.success"
FEEDBACK_RESULT_FAIL_TOPIC = "feedback.result.fail"

logger = logging.getLogger("feedback_producer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

producer: AIOKafkaProducer = None  # 전역으로 선언

async def init_feedback_producer():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retry_backoff_ms=1000,  # 1초마다 재시도
        request_timeout_ms=30000,  # 요청 타임아웃 30초
        acks="all",  # 모든 복제본이 메시지를 받을 때까지 대기 (가장 안전)
        enable_idempotence=True  # 중복 메시지 방지
    )
    await producer.start()

async def close_feedback_producer():
    global producer
    if producer:
        logger.info("Closing feedback producer...")
        await producer.stop()
        producer = None

async def publish_feedback_success(payload) :
    try:
        await producer.send_and_wait(FEEDBACK_RESULT_SUCCESS_TOPIC, value=payload)
        logger.info("Publish feedback success message")
    except Exception as e:
        logger.error(f"Failed to send feedback success message: {e}")
        payload = {
            "userId": payload["userId"],
            "subjectId": payload["subjectId"],
            "type": payload["type"],
            "nth": payload["nth"]
        }
        await publish_feedback_fail(payload, error_code="FEEDBACK_SUCCESS_PUBLISH_FAIL_ERROR", error_message="Failed to publish success message")

async def publish_feedback_fail(original_payload, error_code: str, error_message: str) :
    payload = {
        **original_payload,
        "errorCode": error_code,
        "errorMessage": error_message,
    }
    logger.info("Publish feedback fail message")
    await producer.send_and_wait(FEEDBACK_RESULT_FAIL_TOPIC, value=payload)