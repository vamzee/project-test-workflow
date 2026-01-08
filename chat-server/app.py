from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import logging
import asyncio
from typing import Dict
import httpx
from session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Server")

# Initialize session manager
session_manager = SessionManager()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Configuration
ORCHESTRATOR_URL = "http://localhost:8002"


@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/api/sessions")
async def create_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    return {"session_id": session_id}


@app.get("/api/sessions")
async def get_sessions():
    """Get all chat sessions"""
    return session_manager.get_all_sessions()


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get messages for a specific session"""
    try:
        messages = session_manager.get_messages(session_id)
        return {"messages": messages}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket
    logger.info(f"WebSocket connected for session {session_id}")

    try:
        # Verify session exists
        session_manager.get_session(session_id)

        while True:
            # Receive message from WebSocket
            data = await websocket.receive_json()
            message = data.get("message", "")

            if message:
                # Add user message to session
                session_manager.add_message(session_id, "user", message)

                # Acknowledge receipt
                await websocket.send_json({
                    "type": "ack",
                    "message": "Message received"
                })

                # Send to orchestrator and get response
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{ORCHESTRATOR_URL}/process",
                            json={
                                "session_id": session_id,
                                "message": message
                            }
                        )

                        if response.status_code == 200:
                            response_data = response.json()
                            ai_response = response_data.get("response", "")

                            # Add assistant message to session
                            session_manager.add_message(session_id, "assistant", ai_response)

                            # Send to WebSocket
                            await websocket.send_json({
                                "type": "assistant",
                                "message": ai_response
                            })
                            logger.info(f"Sent AI response for session {session_id}")
                        else:
                            error_msg = "Sorry, I encountered an error processing your request."
                            await websocket.send_json({
                                "type": "assistant",
                                "message": error_msg
                            })
                            logger.error(f"Orchestrator error: {response.status_code}")

                except Exception as e:
                    logger.error(f"Error calling orchestrator: {e}")
                    error_msg = "Sorry, I encountered an error processing your request."
                    await websocket.send_json({
                        "type": "assistant",
                        "message": error_msg
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        if session_id in active_connections:
            del active_connections[session_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
