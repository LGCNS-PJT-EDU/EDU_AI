import logging
import sys

from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from app.config.kafka_config import KAFKA_BOOTSTRAP_SERVERS

logger = logging.getLogger("kafka-admin")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

FEEDBACK_REQUEST_TOPIC = "feedback.request"
FEEDBACK_RESULT_SUCCESS_TOPIC = "feedback.result.success"
FEEDBACK_RESULT_FAIL_TOPIC = "feedback.result.fail"
RECOM_REQUEST_TOPIC = "recom.request"
RECOM_RESULT_SUCCESS_TOPIC = "recom.result.success"
RECOM_RESULT_FAIL_TOPIC = "recom.result.fail"

def initialize_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        client_id="feedback-admin"
    )

    topics_to_create = [
        NewTopic(name=FEEDBACK_REQUEST_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=FEEDBACK_RESULT_SUCCESS_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=FEEDBACK_RESULT_FAIL_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=RECOM_REQUEST_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=RECOM_RESULT_SUCCESS_TOPIC, num_partitions=3, replication_factor=1),
        NewTopic(name=RECOM_RESULT_FAIL_TOPIC, num_partitions=3, replication_factor=1),
    ]

    try:
        existing_topics = admin_client.list_topics()
        logger.info(f"Existing topics: {existing_topics}")

        topics_to_create_filtered = [topic for topic in topics_to_create if topic.name not in existing_topics]

        if topics_to_create_filtered:
            admin_client.create_topics(new_topics=topics_to_create_filtered, validate_only=False)
            for topic in topics_to_create_filtered:
                logger.info(f"Created topic: {topic.name}")
        else:
            logger.info("All topics already exist. No topics created.")

        existing = [t.name for t in topics_to_create if t.name in existing_topics]
        if existing:
            logger.warning(f"Topics already existed and were skipped: {existing}")

    except Exception as e:
        logger.error(f"Failed to create Kafka topics: {e}")
    finally:
        admin_client.close()
