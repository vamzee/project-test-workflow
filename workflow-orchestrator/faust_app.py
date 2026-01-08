import faust
import logging
from supervisor_agent import SupervisorAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faust app
app = faust.App(
    'workflow-orchestrator',
    broker='kafka://localhost:9092',
    value_serializer='json',
)

# Initialize supervisor agent
supervisor = SupervisorAgent()


# Define message models
class ChatRequest(faust.Record):
    session_id: str
    message: str
    timestamp: float = None


class ChatResponse(faust.Record):
    session_id: str
    response: str
    timestamp: float = None


# Define Kafka topics
chat_requests_topic = app.topic('chat-requests', value_type=ChatRequest)
chat_responses_topic = app.topic('chat-responses', value_type=ChatResponse)


@app.agent(chat_requests_topic)
async def process_chat_request(requests):
    """
    Faust agent that processes incoming chat requests
    """
    async for request in requests:
        try:
            logger.info(f"Processing request for session {request.session_id}")

            # Use supervisor agent to process the request
            response_text = supervisor.process_request(
                request.session_id,
                request.message
            )

            # Create response message
            response = ChatResponse(
                session_id=request.session_id,
                response=response_text
            )

            # Send response to output topic
            await chat_responses_topic.send(value=response)

            logger.info(f"Successfully processed request for session {request.session_id}")

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            # Send error response
            error_response = ChatResponse(
                session_id=request.session_id,
                response=f"Sorry, I encountered an error: {str(e)}"
            )
            await chat_responses_topic.send(value=error_response)


@app.timer(interval=30.0)
async def periodic_health_check():
    """
    Periodic health check to keep the app alive
    """
    logger.debug("Health check: Faust app is running")


if __name__ == '__main__':
    app.main()
