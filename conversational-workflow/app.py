from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import os
import json
from dotenv import load_dotenv
from workflow import ConversationalWorkflow

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Conversational Workflow Service")

# Initialize workflow
workflow = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str


@app.on_event("startup")
async def startup_event():
    global workflow

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY is required")

    workflow = ConversationalWorkflow(api_key=api_key)
    logger.info("Conversational Workflow Service started successfully")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "conversational-workflow"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Received chat request for session {request.session_id}")

    try:
        response = workflow.process_message(request.session_id, request.message)

        return ChatResponse(
            session_id=request.session_id,
            response=response
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat responses in real-time"""
    logger.info(f"Received streaming chat request for session {request.session_id}")

    async def generate():
        try:
            async for chunk in workflow.process_message_stream(request.session_id, request.message):
                # Send each chunk as JSON
                yield json.dumps({"chunk": chunk}) + "\n"
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    try:
        workflow.clear_session(session_id)
        return {"message": f"Session {session_id} cleared"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
