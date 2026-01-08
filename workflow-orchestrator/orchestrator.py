from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from supervisor_agent import SupervisorAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Workflow Orchestrator")

# Initialize supervisor agent
supervisor = SupervisorAgent()


class ProcessRequest(BaseModel):
    session_id: str
    message: str


class ProcessResponse(BaseModel):
    session_id: str
    response: str


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "workflow-orchestrator"}


@app.post("/process", response_model=ProcessResponse)
async def process_message(request: ProcessRequest):
    """Process a chat message through the supervisor agent"""
    logger.info(f"Processing request for session {request.session_id}")

    try:
        # Use supervisor agent to process the request
        response = supervisor.process_request(request.session_id, request.message)

        logger.info(f"Successfully processed request for session {request.session_id}")

        return ProcessResponse(
            session_id=request.session_id,
            response=response
        )

    except Exception as e:
        logger.error(f"Error processing request for session {request.session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Workflow Orchestrator API...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
