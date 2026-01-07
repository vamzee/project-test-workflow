# Conversational Workflow

LangGraph-based conversational AI service powered by OpenAI GPT-3.5-turbo.

## Features

- LangGraph workflow for conversation management
- OpenAI GPT-3.5-turbo integration
- Session-based conversation history
- FastAPI HTTP endpoints
- Stateful conversation tracking

## Architecture

```
HTTP Request → LangGraph Workflow → OpenAI API
                      ↓
              [prepare_messages]
                      ↓
                 [call_llm]
                      ↓
              [format_response]
                      ↓
              HTTP Response
```

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Running

```bash
python app.py
```

The service will start on `http://localhost:8001`

## API Endpoints

### POST /chat
Process a chat message

**Request:**
```json
{
  "session_id": "uuid-string",
  "message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "response": "I'm doing well, thank you for asking! How can I help you today?"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "conversational-workflow"
}
```

### DELETE /sessions/{session_id}
Clear conversation history for a session

## Components

### app.py
FastAPI application exposing HTTP endpoints

### workflow.py
LangGraph workflow with three nodes:
1. **prepare_messages**: Retrieves conversation history
2. **call_llm**: Calls OpenAI with conversation context
3. **format_response**: Updates history and formats response

## LangGraph Workflow

```
prepare_messages → call_llm → format_response → END
```

## Session Management

- Each session maintains its own conversation history
- History includes both user and assistant messages
- System prompt sets context for the AI assistant
- Sessions can be cleared using the DELETE endpoint

## Dependencies

- LangGraph: Workflow orchestration
- LangChain: AI framework
- LangChain-OpenAI: OpenAI integration
- OpenAI: API client
- FastAPI: Web framework
- Uvicorn: ASGI server

## OpenAI Configuration

- Model: `gpt-3.5-turbo`
- Temperature: `0.7` (balanced creativity/consistency)
- System prompt: Helpful AI assistant persona
