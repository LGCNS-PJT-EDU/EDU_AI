import asyncio
import logging
import sys
import threading

from kafka import KafkaConsumer
import json

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS
from app.producer.feedback_producer import publish_success, publish_fail

TOPIC_REQUEST = "feedback.request"

logger = logging.getLogger("feedback-request-consumer")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def consume_feedback_messages():
    try:
        logger.info("Consuming feedback messages")

        consumer = KafkaConsumer(
            TOPIC_REQUEST,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="feedback-request-group"
        )

        logger.info("Kafka consumer started for feedback request")

        for message in consumer:
            payload = message.value
            logger.info(f"Received message: {payload}")

            success = False
            last_error = None

            for attempt in range(3):
                try:
                    logger.info(f"Attempt #{attempt + 1}")
                    if True:  # 항상 예외 발생
                        raise Exception("테스트용 강제 오류: Feedback 생성 실패")
                    # 실제 비즈니스 로직(create_feedback 등)이 여기에 들어갑니다.
                    feedback = {
                        "info": {
                            "userId": "5",
                            "date": "2025-05-09",
                            "subject": "HTML"
                        },
                        "scores": {
                            "syntax": 4,
                            "data_types": 3,
                            "OOP": 2,
                            "modules": 1,
                            "exceptions": 10,
                            "total": 20
                        },
                        "feedback": {
                            "strength": {
                              "syntax": "Shows strong grasp of Python syntax",
                              "data_types": "Shows strong grasp of Python data_types",
                              "OOP": "Shows strong grasp of Python OOP",
                              "modules": "Shows strong grasp of Python modules",
                              "exceptions": "Shows strong grasp of Python exceptions"
                            },
                            "weakness": {
                              "syntax": "Needs improvement in Python syntax",
                              "data_types": "Needs improvement in Python data_types",
                              "OOP": "Needs improvement in Python OOP",
                              "modules": "Needs improvement in Python modules",
                              "exceptions": "Needs improvement in Python exceptions"
                            },
                            "final": "Overall solid in Python – focus next on weaker areas."
                        }
                    }
                    result = {
                        **payload,
                        "feedback": feedback
                    }
                    logger.info("Feedback creation succeeded")
                    publish_success(result)
                    success = True
                    break
                except Exception as e:
                    last_error = e
                    logger.error(f"Feedback creation failed (attempt {attempt + 1}): {e}")

            if not success:
                logger.error("Feedback creation failed. Sending to Fail Topic.")
                publish_fail(payload, error_code="FEEDBACK_GEN_ERROR", error_message=str(last_error))

    except Exception as e:
        logger.exception(f"Consumer thread failed: {e}")

def start_feedback_consumer_thread():
    thread = threading.Thread(target=consume_feedback_messages, daemon=True)
    thread.start()