# Agentic Chat Workflow System

A complete enterprise AI solution consisting of three microservices that work together to provide an intelligent chat system using Kafka, LangGraph, and OpenAI.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────────┐
│   Chat Server   │      │  Workflow            │      │  Conversational     │
│   (WebSocket)   │◄────►│  Orchestrator        │◄────►│  Workflow           │
│   + Kafka       │      │  (LangGraph)         │      │  (LangGraph+OpenAI) │
└─────────────────┘      └──────────────────────┘      └─────────────────────┘
        │                          │
        │                          │
        └──────────┬───────────────┘
                   │
              ┌────▼─────┐
              │  Kafka   │
              │ (Topics) │
              └──────────┘
```

## System Components

### 1. Chat Server (Port 8000)
- WebSocket-based chat UI
- Session management (create, view previous sessions)
- Kafka producer (sends user messages to `chat-requests` topic)
- Kafka consumer (receives responses from `chat-responses` topic)
- Real-time bidirectional communication

### 2. Workflow Orchestrator (Kafka Consumer/Producer)
- LangGraph-based supervisory agent
- Consumes from `chat-requests` Kafka topic
- Routes requests to Conversational Workflow via HTTP
- Produces responses to `chat-responses` Kafka topic
- Handles error recovery and response routing

### 3. Conversational Workflow (Port 8001)
- LangGraph workflow with OpenAI integration
- Maintains conversation history per session
- Exposes HTTP API endpoint
- Generates intelligent responses using GPT-3.5-turbo

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenAI API Key

## Installation & Setup

### Step 1: Start Kafka Infrastructure

```bash
# Start Kafka and Zookeeper
docker-compose up -d

# Verify Kafka is running
docker-compose ps

# Check Kafka UI (optional)
# Open http://localhost:8080 in your browser
```

### Step 2: Setup Conversational Workflow Service

```bash
cd conversational-workflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API Key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the service
python app.py
```

The service will start on `http://localhost:8001`

### Step 3: Setup Workflow Orchestrator

Open a new terminal:

```bash
cd workflow-orchestrator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the orchestrator
python orchestrator.py
```

### Step 4: Setup Chat Server

Open a new terminal:

```bash
cd chat-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The chat UI will be available at `http://localhost:8000`

## Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Click "New Chat" to create a new session
3. Type your message and press Enter or click Send
4. The system will:
   - Send your message to Kafka (`chat-requests` topic)
   - Workflow Orchestrator picks it up and forwards to Conversational Workflow
   - Conversational Workflow processes with OpenAI and responds
   - Response flows back through Kafka (`chat-responses` topic)
   - Chat UI displays the response in real-time

## Message Flow

```
User Input → WebSocket → Chat Server → Kafka (chat-requests)
                                            ↓
                                    Orchestrator (LangGraph)
                                            ↓
                                    Conversational Workflow (OpenAI)
                                            ↓
                                    Response Back to Orchestrator
                                            ↓
                                    Kafka (chat-responses)
                                            ↓
                                    Chat Server → WebSocket → User
```

## API Endpoints

### Chat Server (Port 8000)
- `GET /` - Chat UI
- `POST /api/sessions` - Create new chat session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{session_id}/messages` - Get session messages
- `WebSocket /ws/{session_id}` - WebSocket connection for real-time chat

### Conversational Workflow (Port 8001)
- `GET /health` - Health check
- `POST /chat` - Process chat message
- `DELETE /sessions/{session_id}` - Clear session history

## Kafka Topics

- `chat-requests` - User messages from Chat Server
- `chat-responses` - AI responses to Chat Server

## Project Structure

```
chat-workflow/
├── docker-compose.yml           # Kafka infrastructure
├── README.md                    # This file
│
├── chat-server/                 # Project 1
│   ├── app.py                   # FastAPI + WebSocket server
│   ├── session_manager.py       # Session management
│   ├── kafka_handler.py         # Kafka integration
│   ├── requirements.txt
│   └── static/
│       └── index.html           # Chat UI
│
├── workflow-orchestrator/       # Project 2
│   ├── orchestrator.py          # Main orchestrator
│   ├── supervisor_agent.py      # LangGraph supervisor
│   ├── kafka_handler.py         # Kafka integration
│   └── requirements.txt
│
└── conversational-workflow/     # Project 3
    ├── app.py                   # FastAPI server
    ├── workflow.py              # LangGraph workflow
    ├── requirements.txt
    └── .env.example             # Environment variables template
```

## Troubleshooting

### Kafka Connection Issues
```bash
# Check if Kafka is running
docker-compose ps

# View Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

### Service Not Starting
```bash
# Check if ports are available
lsof -i :8000  # Chat Server
lsof -i :8001  # Conversational Workflow
lsof -i :9092  # Kafka

# Check service logs for errors
```

### OpenAI API Issues
- Verify your API key in `conversational-workflow/.env`
- Check your OpenAI account has available credits
- Review logs in the Conversational Workflow terminal

## Stopping the System

```bash
# Stop each Python service with Ctrl+C in their respective terminals

# Stop Kafka infrastructure
docker-compose down

# To remove all data
docker-compose down -v
```

## Features

- Real-time WebSocket communication
- Session-based conversation management
- Kafka-based message queuing
- LangGraph workflow orchestration
- OpenAI integration for intelligent responses
- Persistent conversation history
- Error handling and recovery
- Kafka UI for monitoring (http://localhost:8080)

## Technology Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **Message Queue**: Apache Kafka
- **AI Framework**: LangGraph, LangChain
- **LLM**: OpenAI GPT-3.5-turbo
- **WebSocket**: WebSockets library
- **Containerization**: Docker, Docker Compose

## Next Steps

- Add persistent storage (PostgreSQL/MongoDB)
- Implement authentication and authorization
- Add message encryption
- Deploy to cloud (AWS/GCP/Azure)
- Add monitoring and logging (Prometheus, Grafana)
- Implement rate limiting
- Add more sophisticated LangGraph workflows
- Support for multiple LLM providers

## License

MIT License - Feel free to use this for learning and development.
