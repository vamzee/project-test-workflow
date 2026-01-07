import logging
import time
from kafka_handler import KafkaHandler
from supervisor_agent import SupervisorAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    def __init__(self):
        self.kafka_handler = KafkaHandler()
        self.supervisor = SupervisorAgent()

    def start(self):
        logger.info("Starting Workflow Orchestrator...")

        # Connect Kafka components
        self.kafka_handler.connect_producer()
        self.kafka_handler.connect_consumer(
            topic='chat-requests',
            group_id='orchestrator-group'
        )

        logger.info("Workflow Orchestrator started successfully")
        logger.info("Waiting for requests...")

        try:
            # Start consuming requests
            self.kafka_handler.consume_requests(self.handle_request)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.kafka_handler.close()

    def handle_request(self, session_id: str, user_message: str):
        logger.info(f"Processing request for session {session_id}")

        try:
            # Use supervisor agent to process the request
            response = self.supervisor.process_request(session_id, user_message)

            # Send response back to Kafka
            self.kafka_handler.send_response(session_id, response)
            logger.info(f"Successfully processed request for session {session_id}")

        except Exception as e:
            logger.error(f"Error processing request for session {session_id}: {e}")
            error_response = f"Sorry, I encountered an error processing your request."
            self.kafka_handler.send_response(session_id, error_response)


if __name__ == "__main__":
    orchestrator = WorkflowOrchestrator()

    # Wait a bit for Kafka to be ready
    logger.info("Waiting 5 seconds for Kafka to be ready...")
    time.sleep(5)

    orchestrator.start()
