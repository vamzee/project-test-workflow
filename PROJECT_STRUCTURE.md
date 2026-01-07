# Project Structure

Complete file structure of the Agentic Chat Workflow System.

```
chat-workflow/
│
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── PROJECT_STRUCTURE.md               # This file
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Kafka infrastructure
├── setup-all.sh                       # Automated setup script
├── start-all.sh                       # Start Kafka script
│
├── chat-server/                       # Project 1: Chat Server
│   ├── README.md                      # Chat server documentation
│   ├── requirements.txt               # Python dependencies
│   ├── run.sh                         # Run script
│   ├── app.py                         # Main FastAPI application
│   ├── session_manager.py             # Session management logic
│   ├── kafka_handler.py               # Kafka producer/consumer
│   └── static/
│       └── index.html                 # Chat UI (HTML/CSS/JS)
│
├── workflow-orchestrator/             # Project 2: Workflow Orchestrator
│   ├── README.md                      # Orchestrator documentation
│   ├── requirements.txt               # Python dependencies
│   ├── run.sh                         # Run script
│   ├── orchestrator.py                # Main orchestrator
│   ├── supervisor_agent.py            # LangGraph supervisor
│   └── kafka_handler.py               # Kafka integration
│
└── conversational-workflow/           # Project 3: Conversational Workflow
    ├── README.md                      # Workflow documentation
    ├── requirements.txt               # Python dependencies
    ├── run.sh                         # Run script
    ├── .env.example                   # Environment template
    ├── app.py                         # FastAPI server
    └── workflow.py                    # LangGraph workflow
```

## File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Complete system documentation |
| `QUICKSTART.md` | Fast setup guide |
| `docker-compose.yml` | Kafka/Zookeeper configuration |
| `setup-all.sh` | Automated installation script |
| `start-all.sh` | Start Kafka infrastructure |
| `.gitignore` | Git ignore patterns |

### Chat Server

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | FastAPI + WebSocket server | ~150 |
| `session_manager.py` | Session/message management | ~70 |
| `kafka_handler.py` | Kafka producer/consumer | ~90 |
| `static/index.html` | Full chat UI | ~350 |

**Key Features:**
- WebSocket real-time communication
- In-memory session storage
- Kafka integration
- Responsive UI with session management

### Workflow Orchestrator

| File | Purpose | Lines |
|------|---------|-------|
| `orchestrator.py` | Main entry point | ~60 |
| `supervisor_agent.py` | LangGraph supervisor agent | ~100 |
| `kafka_handler.py` | Kafka consumer/producer | ~70 |

**Key Features:**
- LangGraph state management
- HTTP client for service calls
- Error handling and recovery
- Kafka message routing

### Conversational Workflow

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | FastAPI HTTP server | ~70 |
| `workflow.py` | LangGraph workflow | ~120 |
| `.env.example` | Environment template | ~1 |

**Key Features:**
- OpenAI integration
- Conversation history management
- LangGraph workflow
- RESTful API

## Technology Stack by Project

### Chat Server
- **Framework:** FastAPI
- **Real-time:** WebSockets
- **Message Queue:** kafka-python
- **Frontend:** Vanilla JavaScript

### Workflow Orchestrator
- **Workflow:** LangGraph
- **Framework:** LangChain
- **Message Queue:** kafka-python
- **HTTP:** requests

### Conversational Workflow
- **Workflow:** LangGraph
- **AI:** LangChain + OpenAI
- **Framework:** FastAPI
- **Config:** python-dotenv

## Dependencies Summary

### Common Dependencies
- Python 3.9+
- kafka-python 2.0.2
- pydantic 2.5.3

### LangGraph Projects (Orchestrator + Workflow)
- langgraph 0.2.28
- langchain 0.1.0
- langchain-core 0.1.10

### Web Services (Chat Server + Workflow)
- fastapi 0.109.0
- uvicorn 0.27.0

### AI-Specific (Conversational Workflow)
- langchain-openai 0.0.2
- openai 1.10.0

## Ports Used

| Service | Port | Protocol |
|---------|------|----------|
| Chat Server | 8000 | HTTP/WebSocket |
| Conversational Workflow | 8001 | HTTP |
| Kafka | 9092 | TCP |
| Zookeeper | 2181 | TCP |
| Kafka UI | 8080 | HTTP |

## Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `chat-requests` | Chat Server | Orchestrator | User messages |
| `chat-responses` | Orchestrator | Chat Server | AI responses |

## Virtual Environments

Each project has its own isolated virtual environment:
- `chat-server/venv/`
- `workflow-orchestrator/venv/`
- `conversational-workflow/venv/`

This ensures no dependency conflicts between projects.

## Data Flow

```
User Input (Browser)
    ↓ WebSocket
Chat Server (8000)
    ↓ Kafka Producer
chat-requests topic
    ↓ Kafka Consumer
Workflow Orchestrator
    ↓ HTTP POST
Conversational Workflow (8001)
    ↓ OpenAI API
GPT-3.5-turbo
    ↓ Response
Conversational Workflow
    ↓ HTTP Response
Workflow Orchestrator
    ↓ Kafka Producer
chat-responses topic
    ↓ Kafka Consumer
Chat Server
    ↓ WebSocket
User Browser
```

## Lines of Code

| Component | Python | HTML/CSS/JS | Config |
|-----------|--------|-------------|--------|
| Chat Server | ~310 | ~350 | ~10 |
| Orchestrator | ~230 | 0 | ~10 |
| Workflow | ~190 | 0 | ~10 |
| **Total** | **~730** | **~350** | **~30** |

## Setup Time

- Kafka startup: ~30 seconds
- Python dependencies install: ~2-3 minutes per project
- Total setup time: ~10-15 minutes (one-time)
- Startup time: ~1 minute (after setup)
