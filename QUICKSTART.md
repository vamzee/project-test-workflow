# Quick Start Guide

Get the Agentic Chat Workflow System running in 5 minutes!

## Prerequisites Check

```bash
# Check Python (need 3.9+)
python3 --version

# Check Docker
docker --version
docker-compose --version
```

## Quick Setup (Automated)

```bash
# 1. Run automated setup
./setup-all.sh

# 2. Add your OpenAI API key
nano conversational-workflow/.env
# Add: OPENAI_API_KEY=sk-your-key-here

# 3. Start Kafka
./start-all.sh
```

## Manual 3-Step Process

### Step 1: Start Kafka (30 seconds)

```bash
docker-compose up -d
sleep 30
```

### Step 2: Start Services (3 terminals)

**Terminal 1 - Conversational Workflow:**
```bash
cd conversational-workflow
source venv/bin/activate
export OPENAI_API_KEY=sk-your-key-here
python app.py
```

**Terminal 2 - Workflow Orchestrator:**
```bash
cd workflow-orchestrator
source venv/bin/activate
python orchestrator.py
```

**Terminal 3 - Chat Server:**
```bash
cd chat-server
source venv/bin/activate
python app.py
```

### Step 3: Use the Chat

1. Open http://localhost:8000
2. Click "New Chat"
3. Start chatting!

## Verification

Check all services are running:

```bash
# Kafka
docker-compose ps

# Conversational Workflow
curl http://localhost:8001/health

# Chat Server (open in browser)
open http://localhost:8000
```

## Monitoring

- Chat UI: http://localhost:8000
- Kafka UI: http://localhost:8080
- Conversational API: http://localhost:8001/health

## Troubleshooting

### Kafka not starting?
```bash
docker-compose down -v
docker-compose up -d
```

### Python module not found?
```bash
cd <project-directory>
source venv/bin/activate
pip install -r requirements.txt
```

### OpenAI error?
Check your API key in `conversational-workflow/.env`

## Stop Everything

```bash
# Stop Python services: Ctrl+C in each terminal

# Stop Kafka
docker-compose down
```

## What's Happening?

1. You type a message in the chat UI (port 8000)
2. Message goes to Kafka topic `chat-requests`
3. Orchestrator picks it up and sends to Conversational Workflow (port 8001)
4. OpenAI processes and responds
5. Response goes to Kafka topic `chat-responses`
6. Chat UI displays the response

That's it! For more details, see README.md
