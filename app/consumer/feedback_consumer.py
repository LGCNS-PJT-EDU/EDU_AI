import asyncio
import logging
import sys

import json

from aiokafka.errors import CommitFailedError

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS
from app.producer.feedback_producer import publish_feedback_success, publish_feedback_fail
from app.routers.feedback_router import generate_feedback
from aiokafka import AIOKafkaConsumer

FEEDBACK_REQUEST_TOPIC = "feedback.request"

logger = logging.getLogger("feedback-request-consumer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def consume_feedback():
    consumer = AIOKafkaConsumer(
        FEEDBACK_REQUEST_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",  # 수정
        enable_auto_commit=False,  # 수동 커밋 권장
        group_id="feedback-request-group",
        max_poll_interval_ms=900000,
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000,
        request_timeout_ms=60000
    )
    await consumer.start()
    logger.info("Consumer started.")
    try:
        async for message in consumer:
            payload = message.value
            logger.info(f"Received: {payload}")
            user_id = payload["userId"]
            subject_id = payload["subjectId"]
            feedback_type = payload["type"]
            nth = payload["nth"] if payload["nth"] is not None else 0

            success = False
            last_error = None
            result = None
            for attempt in range(3):
                try:
                    logger.info(f"Attempt #{attempt + 1}")
                    feedback = await generate_feedback(user_id, subject_id, feedback_type, nth)
                    logger.info(f"Feedback: {feedback}")
                    result = {
                        **payload,
                        "feedback": feedback
                    }
                    logger.info(f"Feedback result: {result}")
                    logger.info("Feedback creation succeeded")
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Feedback creation failed (attempt {attempt + 1}): {e}")
                    last_error = e
                    await asyncio.sleep(1)
            try:
                if not success:
                        await publish_feedback_fail(payload, error_code="FEEDBACK_GEN_ERROR", error_message=str(last_error))
                else:
                    await publish_feedback_success(result)
                await consumer.commit()
            except Exception as e:  # ✅ 모든 예외 처리
                logger.error(f"publish 또는 commit 중 예외 발생: {type(e).__name__} - {e}")
                raise e
    finally:
        await consumer.stop()
        logger.info("Consumer stopped.")

async def run_feedback_consumer_with_restart(retries=3, delay=5):
    for i in range(retries):
        try:
            logger.info(f"Feedback Consumer 시작 (attemp {i + 1})/retries")
            await consume_feedback()
            break
        except Exception as e:
            logger.error(f"예외 발생: {type(e).__name__} - {e}")
            logger.info(f"{delay}초 후 재시도...")
            await asyncio.sleep(delay)
    else:
        logger.critical("재시도 3회 실패로 Feedback Consumer 종료")