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
    is_chunk: bool = False
    is_done: bool = False


# Define Kafka topics
chat_requests_topic = app.topic('chat-requests', value_type=ChatRequest)
chat_responses_topic = app.topic('chat-responses', value_type=ChatResponse)


@app.agent(chat_requests_topic)
async def process_chat_request(requests):
    """
    Faust agent that processes incoming chat requests with streaming
    """
    async for request in requests:
        try:
            logger.info(f"Processing streaming request for session {request.session_id}")

            # Use supervisor agent to process the request with streaming
            async for chunk in supervisor.process_request_stream(
                request.session_id,
                request.message
            ):
                # Send each chunk to Kafka
                chunk_response = ChatResponse(
                    session_id=request.session_id,
                    response=chunk,
                    is_chunk=True,
                    is_done=False
                )
                await chat_responses_topic.send(value=chunk_response)

            # Send final "done" message
            done_response = ChatResponse(
                session_id=request.session_id,
                response="",
                is_chunk=False,
                is_done=True
            )
            await chat_responses_topic.send(value=done_response)

            logger.info(f"Successfully processed streaming request for session {request.session_id}")

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            # Send error response
            error_response = ChatResponse(
                session_id=request.session_id,
                response=f"Sorry, I encountered an error: {str(e)}",
                is_chunk=False,
                is_done=True
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
