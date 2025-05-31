import asyncio
import logging
import sys

import json

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS
from app.producer.feedback_producer import publish_success, publish_fail
from app.routers.feedback_router import generate_feedback
from aiokafka import AIOKafkaConsumer

TOPIC_REQUEST = "feedback.request"

logger = logging.getLogger("feedback-request-consumer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def consume_feedback():
    consumer = AIOKafkaConsumer(
        TOPIC_REQUEST,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",  # 수정
        enable_auto_commit=False,  # 수동 커밋 권장
        group_id="feedback-request-group",
    )
    await consumer.start()
    logger.info("Consumer started.")
    try:
        async for message in consumer:
            payload = message.value
            logger.info(f"Received: {payload}")
            user_id = payload["userId"]
            subject_id = payload["subjectId"]

            success = False
            last_error = None

            for attempt in range(3):
                try:
                    logger.info(f"Attempt #{attempt + 1}")
                    # if True:  # 항상 예외 발생
                    #     raise Exception("테스트용 강제 오류: Feedback 생성 실패")
                    # 실제 비즈니스 로직(create_feedback 등)이 여기에 들어갑니다.
                    feedback = await generate_feedback(user_id, subject_id)
                    logger.info(f"Feedback: {feedback}")
                    result = {
                        **payload,
                        "feedback": feedback
                    }
                    logger.info(f"Feedback result: {result}")
                    logger.info("Feedback creation succeeded")
                    await publish_success(result)
                    success = True
                    await consumer.commit()
                    break
                except Exception as e:
                    logger.error(f"Feedback creation failed (attempt {attempt + 1}): {e}")
                    last_error = e
                    await asyncio.sleep(1)
            if not success:
                await publish_fail(payload, error_code="FEEDBACK_GEN_ERROR", error_message=str(last_error))
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        await consumer.stop()
        logger.info("Consumer stopped.")