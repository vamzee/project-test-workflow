from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import logging
import asyncio
from typing import Dict
from session_manager import SessionManager
from kafka_handler import KafkaHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chat Server")

# Initialize managers
session_manager = SessionManager()
kafka_handler = KafkaHandler()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Store streaming message buffers (accumulate chunks)
streaming_buffers: Dict[str, str] = {}

# Store reference to main event loop
main_event_loop = None


@app.on_event("startup")
async def startup_event():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    logger.info("Starting chat server...")
    kafka_handler.connect()
    kafka_handler.start_consumer(handle_kafka_response)
    logger.info("Chat server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    kafka_handler.stop()
    logger.info("Chat server shutdown")


def handle_kafka_response(session_id: str, response: str, is_chunk: bool = False, is_done: bool = False):
    """Callback for Kafka consumer to handle responses (including streaming chunks)"""

    # Initialize buffer for this session if needed
    if session_id not in streaming_buffers:
        streaming_buffers[session_id] = ""

    # Accumulate chunks
    if is_chunk and response:
        streaming_buffers[session_id] += response

    # When streaming is done, save complete message
    if is_done:
        complete_message = streaming_buffers[session_id]
        if complete_message:
            session_manager.add_message(session_id, "assistant", complete_message)
        # Clear buffer
        streaming_buffers[session_id] = ""

    # Send to WebSocket if connected
    if session_id in active_connections:
        websocket = active_connections[session_id]
        try:
            if main_event_loop:
                asyncio.run_coroutine_threadsafe(
                    send_streaming_to_websocket(websocket, response, is_chunk, is_done),
                    main_event_loop
                )
            else:
                logger.error("Main event loop not available")
        except Exception as e:
            logger.error(f"Error scheduling WebSocket message: {e}")


async def send_message_to_websocket(websocket: WebSocket, message: str):
    try:
        await websocket.send_json({
            "type": "assistant",
            "message": message
        })
    except Exception as e:
        logger.error(f"Failed to send message via WebSocket: {e}")


async def send_streaming_to_websocket(websocket: WebSocket, chunk: str, is_chunk: bool, is_done: bool):
    try:
        if is_chunk and chunk:
            # Send chunk
            await websocket.send_json({
                "type": "assistant_chunk",
                "chunk": chunk
            })
        elif is_done:
            # Send done signal
            await websocket.send_json({
                "type": "assistant_done"
            })
    except Exception as e:
        logger.error(f"Failed to send streaming message via WebSocket: {e}")


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

                # Send to Kafka
                kafka_handler.send_request(session_id, message)

                # Acknowledge receipt
                await websocket.send_json({
                    "type": "ack",
                    "message": "Message received"
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
