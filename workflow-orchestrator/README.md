# Workflow Orchestrator

LangGraph-based orchestrator with a supervisory agent that routes messages between Kafka and the Conversational Workflow service.

## Features

- LangGraph supervisory agent
- Kafka consumer for incoming requests
- Kafka producer for outgoing responses
- HTTP client to communicate with Conversational Workflow
- Error handling and recovery

## Architecture

```
Kafka (chat-requests) → Supervisor Agent → HTTP Request → Conversational Workflow
                              ↓
                    (Response Processing)
                              ↓
                Kafka (chat-responses)
```

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python orchestrator.py
```

The orchestrator will start consuming from Kafka `chat-requests` topic.

## Components

### orchestrator.py
Main entry point that connects Kafka and supervisor agent

### supervisor_agent.py
LangGraph-based agent that orchestrates the workflow:
1. Receives request
2. Calls conversational workflow service
3. Handles response or error
4. Returns result

### kafka_handler.py
Manages Kafka consumer and producer connections

## LangGraph Workflow

```
START → receive_request → call_conversational_workflow
                               ↓
                       [Success/Error?]
                        ↓            ↓
               handle_response  handle_error
                        ↓            ↓
                           END
```

## Configuration

- Kafka bootstrap server: `localhost:9092`
- Conversational Workflow URL: `http://localhost:8001`
- Consumer group: `orchestrator-group`

## Dependencies

- LangGraph: Workflow orchestration
- LangChain: Agent framework
- kafka-python: Kafka client
- requests: HTTP client
