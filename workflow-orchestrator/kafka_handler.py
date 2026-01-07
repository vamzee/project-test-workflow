import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from typing import Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaHandler:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None

    def connect_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_block_ms=5000
            )
            logger.info("Kafka producer connected")
        except Exception as e:
            logger.error(f"Failed to connect Kafka producer: {e}")
            raise

    def connect_consumer(self, topic: str, group_id: str):
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                group_id=group_id,
                enable_auto_commit=True
            )
            logger.info(f"Kafka consumer connected to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to connect Kafka consumer: {e}")
            raise

    def send_response(self, session_id: str, response: str):
        if not self.producer:
            raise Exception("Kafka producer not connected")

        payload = {
            "session_id": session_id,
            "response": response
        }

        try:
            future = self.producer.send('chat-responses', value=payload)
            future.get(timeout=10)
            logger.info(f"Sent response to Kafka for session {session_id}")
        except KafkaError as e:
            logger.error(f"Failed to send response to Kafka: {e}")
            raise

    def consume_requests(self, callback: Callable):
        logger.info("Starting to consume requests...")

        for message in self.consumer:
            try:
                data = message.value
                session_id = data.get('session_id')
                user_message = data.get('message')

                logger.info(f"Received request for session {session_id}: {user_message}")
                callback(session_id, user_message)
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")

    def close(self):
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        logger.info("Kafka handler closed")
