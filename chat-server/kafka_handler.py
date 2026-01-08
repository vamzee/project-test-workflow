import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from threading import Thread
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaHandler:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None
        self.running = False
        self.message_callbacks = {}

    def connect(self):
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

    def send_request(self, session_id: str, message: str):
        if not self.producer:
            raise Exception("Kafka producer not connected")

        payload = {
            "session_id": session_id,
            "message": message,
            "timestamp": time.time()
        }

        try:
            future = self.producer.send('chat-requests', value=payload)
            future.get(timeout=10)
            logger.info(f"Sent message to Kafka for session {session_id}")
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            raise

    def start_consumer(self, callback):
        self.running = True
        thread = Thread(target=self._consume_responses, args=(callback,))
        thread.daemon = True
        thread.start()
        logger.info("Kafka consumer thread started")

    def _consume_responses(self, callback):
        try:
            self.consumer = KafkaConsumer(
                'chat-responses',
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                group_id='chat-server-group',
                enable_auto_commit=True
            )
            logger.info("Kafka consumer connected to chat-responses topic")

            for message in self.consumer:
                if not self.running:
                    break

                try:
                    data = message.value
                    session_id = data.get('session_id')
                    response = data.get('response', '')
                    is_chunk = data.get('is_chunk', False)
                    is_done = data.get('is_done', False)

                    if is_chunk:
                        logger.debug(f"Received chunk for session {session_id}")
                    elif is_done:
                        logger.info(f"Received done signal for session {session_id}")
                    else:
                        logger.info(f"Received response for session {session_id}")

                    callback(session_id, response, is_chunk, is_done)
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")

    def stop(self):
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        logger.info("Kafka handler stopped")
