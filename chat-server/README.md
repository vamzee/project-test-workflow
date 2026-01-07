# Chat Server

WebSocket-based chat server with Kafka integration and session management.

## Features

- Real-time WebSocket communication
- Session management (create, view, and switch between sessions)
- Kafka producer for sending user messages
- Kafka consumer for receiving AI responses
- Beautiful, responsive chat UI

## Architecture

```
User Browser (WebSocket) ←→ FastAPI Server ←→ Kafka
                                                 ↓
                                         (chat-requests topic)
                                                 ↑
                                         (chat-responses topic)
```

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

The server will start on `http://localhost:8000`

## API Endpoints

- `GET /` - Chat UI
- `POST /api/sessions` - Create a new chat session
- `GET /api/sessions` - Get all sessions
- `GET /api/sessions/{session_id}/messages` - Get messages for a session
- `WebSocket /ws/{session_id}` - WebSocket connection for real-time chat

## Components

### app.py
Main FastAPI application with WebSocket support

### session_manager.py
Manages chat sessions and message history in-memory

### kafka_handler.py
Handles Kafka producer/consumer operations

### static/index.html
Chat UI with session management

## Usage Flow

1. User creates a new session via UI
2. User sends a message through WebSocket
3. Server publishes message to Kafka `chat-requests` topic
4. Server listens on `chat-responses` topic for responses
5. When response arrives, it's sent back to user via WebSocket
6. Message is stored in session history

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- WebSockets: Real-time communication
- kafka-python: Kafka client
