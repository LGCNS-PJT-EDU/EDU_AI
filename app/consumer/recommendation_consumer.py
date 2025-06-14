import asyncio
import json
import logging
import sys

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS
from app.producer.recommendation_producer import publish_recommendation_fail, publish_recommendation_success
from app.routers.recommendation_router import recommend_content

RECOM_REQUEST_TOPIC = "recom.request"

logger = logging.getLogger("recommend-request-consumer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def consume_recommend():
    from aiokafka import AIOKafkaConsumer
    consumer = AIOKafkaConsumer(
        RECOM_REQUEST_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="recom-request-group",
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

            success = False
            last_error = None
            result = None
            for attempt in range(3):
                try:
                    logger.info(f"Attempt #{attempt + 1}")
                    recommendation = await recommend_content(user_id, subject_id)
                    logger.info(f"Recommendation: {recommendation}")
                    result = {
                        **payload,
                        "recommendation": recommendation
                    }
                    logger.info(f"Recommendation result: {result}")
                    logger.info("Recommendation creation succeeded")
                    success = True
                    break
                except Exception as e:
                    logger.error(f"Recommendation creation failed (attempt {attempt + 1}): {e}")
                    last_error = e
                    await asyncio.sleep(1)
            try:
                if not success:
                    await publish_recommendation_fail(payload, error_code="RECOM_GEN_ERROR", error_message=str(last_error))
                else:
                    await publish_recommendation_success(result)
                await consumer.commit()
            except Exception as e:  # ✅ 모든 예외 처리
                logger.error(f"publish 또는 commit 중 예외 발생: {type(e).__name__} - {e}")
                raise e
    finally:
        await consumer.stop()
        logger.info("Consumer stopped.")

async def run_recommend_consumer_with_restart(retries=3, delay=5):
    for i in range(retries):
        try:
            logger.info(f"Recommend Consumer 시작 (attemp {i + 1})/retries")
            await consume_recommend()
            break
        except Exception as e:
            logger.error(f"예외 발생: {type(e).__name__} - {e}")
            logger.info(f"{delay}초 후 재시도...")
            await asyncio.sleep(delay)
    else:
        logger.critical("재시도 3회 실패로 Recommend Consumer 종료")