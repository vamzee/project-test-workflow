# Chat Workflow Architecture - Complete Flow Explanation

## Overview
This is a distributed agentic chat system using **Faust stream processing**, **Kafka**, **LangGraph**, and **OpenAI GPT-3.5-turbo**. It consists of three main services working together.

---

## 1. SESSION CREATION FLOW

### Step-by-Step Process:

```
┌─────────────┐          POST /api/sessions          ┌─────────────────┐
│   Browser   │ ──────────────────────────────────> │  chat-server    │
│   (User)    │                                       │   (Port 8000)   │
└─────────────┘                                       └─────────────────┘
                                                              │
                                                              │ Calls
                                                              ▼
                                                      ┌─────────────────┐
                                                      │ SessionManager  │
                                                      │  .create_session()
                                                      └─────────────────┘
                                                              │
                                                              │ Generates
                                                              ▼
                                                      session_id = uuid.uuid4()
                                                      Example: "c1074788-0ce6-4d24-..."
```

### Code Location: `chat-server/session_manager.py`

```python
def create_session(self) -> str:
    session_id = str(uuid.uuid4())                    # 1. Generate unique UUID
    self.sessions[session_id] = ChatSession(          # 2. Create ChatSession object
        session_id=session_id,
        created_at=datetime.now().isoformat()
    )
    return session_id                                  # 3. Return to user
```

### What Happens:
1. **User opens the chat UI** at `http://localhost:8000`
2. **Browser JavaScript calls** `POST /api/sessions`
3. **SessionManager generates** a unique UUID (e.g., `c1074788-0ce6-4d24-a170-2e64736ab7b3`)
4. **Creates in-memory ChatSession** object with empty message list
5. **Returns session_id** to the browser
6. **Browser stores** session_id and uses it for WebSocket connection

---

## 2. MESSAGE FLOW - Complete Journey

### The Complete Path from User to OpenAI and Back:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          COMPLETE MESSAGE FLOW                                │
└──────────────────────────────────────────────────────────────────────────────┘

 Step 1: User Sends Message
 ──────────────────────────

    ┌─────────────┐     WebSocket: "Hello!"      ┌──────────────────┐
    │   Browser   │ ──────────────────────────> │  chat-server     │
    │             │  ws://localhost:8000/ws/{id}  │  (Port 8000)     │
    └─────────────┘                               └──────────────────┘
                                                          │
                                                          │ 1a. Store message
                                                          ▼
                                                  session_manager.add_message(
                                                      session_id,
                                                      "user",
                                                      "Hello!"
                                                  )

 Step 2: Publish to Kafka
 ────────────────────────

    ┌──────────────────┐                          ┌──────────────────┐
    │  chat-server     │    Kafka Topic:          │     Kafka        │
    │  kafka_handler   │  "chat-requests"         │  (Port 9092)     │
    │                  │ ────────────────────────> │                  │
    └──────────────────┘                          └──────────────────┘
                            Message Payload:
                            {
                              "session_id": "c1074788...",
                              "message": "Hello!",
                              "timestamp": 1767843519.948
                            }

 Step 3: Faust Stream Processing
 ───────────────────────────────

    ┌──────────────────┐                          ┌──────────────────────┐
    │     Kafka        │   Faust Consumer         │ workflow-orchestrator │
    │  "chat-requests" │ ────────────────────────> │   Faust Worker       │
    │    Topic         │                           │                      │
    └──────────────────┘                          └──────────────────────┘
                                                           │
                                                           │ Faust Agent:
                                                           │ @app.agent(chat_requests_topic)
                                                           │ async def process_chat_request()
                                                           ▼
                                                   ┌──────────────────────┐
                                                   │  supervisor_agent    │
                                                   │  .process_request()  │
                                                   └──────────────────────┘

 Step 4: LangGraph Supervisor Orchestration
 ──────────────────────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │  supervisor_agent    │   HTTP POST          │ conversational-      │
    │  (LangGraph)         │   /chat              │ workflow             │
    │                      │ ───────────────────> │ (Port 8001)          │
    └──────────────────────┘                      └──────────────────────┘
                                Request Body:
                                {
                                  "session_id": "c1074788...",
                                  "message": "Hello!"
                                }

 Step 5: OpenAI LLM Call (THE MAGIC!)
 ────────────────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │ conversational-      │   OpenAI API         │   OpenAI GPT-3.5     │
    │ workflow             │   self.llm.invoke()  │                      │
    │ (LangGraph)          │ ───────────────────> │  api.openai.com      │
    └──────────────────────┘                      └──────────────────────┘
                                Messages:
                                [
                                  SystemMessage("You are a helpful AI..."),
                                  HumanMessage("Hello!")
                                ]

                                Response:
                                "Hi! How can I help you today?"

 Step 6: Response Flows Back
 ───────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │ conversational-      │   HTTP Response      │  supervisor_agent    │
    │ workflow             │ <─────────────────── │  (LangGraph)         │
    └──────────────────────┘                      └──────────────────────┘
                                                           │
                                                           │ Returns to
                                                           ▼
                                                   ┌──────────────────────┐
                                                   │  Faust Worker        │
                                                   │  process_chat_request│
                                                   └──────────────────────┘

 Step 7: Publish Response to Kafka
 ─────────────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │  Faust Worker        │   Kafka Topic:       │     Kafka            │
    │                      │  "chat-responses"    │  (Port 9092)         │
    │                      │ ───────────────────> │                      │
    └──────────────────────┘                      └──────────────────────┘
                            Message Payload:
                            {
                              "session_id": "c1074788...",
                              "response": "Hi! How can I help you today?"
                            }

 Step 8: Chat Server Receives Response
 ─────────────────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │     Kafka            │   Kafka Consumer     │  chat-server         │
    │  "chat-responses"    │ ───────────────────> │  kafka_handler       │
    │    Topic             │                       │  (Consumer Thread)   │
    └──────────────────────┘                      └──────────────────────┘
                                                           │
                                                           │ Callback:
                                                           │ handle_kafka_response()
                                                           ▼
                                                   1. Store in session_manager
                                                   2. Send to WebSocket

 Step 9: WebSocket Delivery to User
 ──────────────────────────────────

    ┌──────────────────────┐                      ┌──────────────────────┐
    │  chat-server         │   WebSocket Send     │   Browser            │
    │  send_message_to_    │ ───────────────────> │   (User)             │
    │  websocket()         │                       │                      │
    └──────────────────────┘                      └──────────────────────┘
                            Message:
                            {
                              "type": "assistant",
                              "message": "Hi! How can I help you today?"
                            }
```

---

## 3. WORKFLOW-ORCHESTRATOR'S ROLE (The Supervisor)

### What It Does:

The **workflow-orchestrator** is the intelligent middleware that uses **LangGraph** to orchestrate the conversation flow. It acts as a supervisor that can potentially:

1. **Route messages** to appropriate services
2. **Handle errors** gracefully
3. **Add business logic** before/after LLM calls
4. **Scale** by adding more conversational agents
5. **Track state** and make decisions

### Current LangGraph Flow:

```
┌──────────────────────────────────────────────────────────────┐
│            SUPERVISOR AGENT (LangGraph State Graph)          │
└──────────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌─────────────────┐
│ receive_request │  ← Logs the incoming request
└─────────────────┘
      │
      ▼
┌──────────────────────────────┐
│ call_conversational_workflow │  ← Makes HTTP POST to conversational-workflow
└──────────────────────────────┘
      │
      │ Conditional Edge: Success or Error?
      ├────────────┬──────────────┐
      │ SUCCESS    │    ERROR     │
      ▼            ▼              ▼
┌──────────────┐        ┌──────────────┐
│handle_response│        │ handle_error │
└──────────────┘        └──────────────┘
      │                        │
      └────────────┬───────────┘
                   ▼
                  END
```

### Code Location: `workflow-orchestrator/supervisor_agent.py`

**Key Methods:**

```python
def process_request(self, session_id: str, user_message: str) -> str:
    # Entry point called by Faust agent
    initial_state = AgentState(
        session_id=session_id,
        user_message=user_message,
        response="",
        error=""
    )

    # Run the LangGraph workflow
    final_state = self.graph.invoke(initial_state)

    return final_state["response"]
```

**Why Use LangGraph Here?**

- **Flexibility**: Easy to add more nodes (e.g., "check_user_intent", "select_specialist_agent")
- **State Management**: Track conversation state across multiple steps
- **Error Handling**: Built-in error paths
- **Scalability**: Can extend to multi-agent systems where supervisor routes to different specialized agents

### Faust Integration:

```python
# File: workflow-orchestrator/faust_app.py

@app.agent(chat_requests_topic)
async def process_chat_request(requests):
    """Faust agent that consumes from Kafka and processes messages"""
    async for request in requests:
        # Call the supervisor agent
        response_text = supervisor.process_request(
            request.session_id,
            request.message
        )

        # Send response back to Kafka
        response = ChatResponse(
            session_id=request.session_id,
            response=response_text
        )
        await chat_responses_topic.send(value=response)
```

**Faust's Role:**
- **Stream Processing**: Consumes Kafka streams in real-time
- **Async Processing**: Non-blocking, high-throughput
- **Scalability**: Can run multiple workers for parallel processing
- **Reliability**: Kafka offset management ensures no message loss

---

## 4. OPENAI LLM CALL LOCATION

### Exact Location: `conversational-workflow/workflow.py` Lines 62-90

```python
def call_llm(self, state: ConversationState) -> ConversationState:
    logger.info(f"Calling OpenAI LLM for session {state['session_id']}")

    # Build messages for LLM
    messages = [
        SystemMessage(content="You are a helpful AI assistant...")
    ]

    # Add chat history (context from previous messages)
    for msg in state["chat_history"]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Add current message
    messages.append(HumanMessage(content=state["message"]))

    try:
        # ⭐ THIS IS WHERE THE OPENAI API IS CALLED ⭐
        response = self.llm.invoke(messages)
        state["response"] = response.content

    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        state["response"] = "I apologize, but I'm having trouble..."

    return state
```

### LLM Initialization:

```python
# File: conversational-workflow/workflow.py Lines 25-29

self.llm = ChatOpenAI(
    model="gpt-3.5-turbo",          # OpenAI model
    temperature=0.7,                 # Creativity level
    openai_api_key=self.api_key     # Your API key from .env
)
```

### The LLM Flow in Conversational-Workflow:

```
┌──────────────────────────────────────────────────────────────┐
│        CONVERSATIONAL WORKFLOW (LangGraph State Graph)       │
└──────────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌──────────────────┐
│ prepare_messages │  ← Retrieve chat history for this session
└──────────────────┘
      │
      ▼
┌──────────────────┐
│    call_llm      │  ← ⭐ CALLS OpenAI API ⭐
└──────────────────┘      self.llm.invoke(messages)
      │                   └─> api.openai.com
      ▼
┌──────────────────┐
│ format_response  │  ← Save message + response to session history
└──────────────────┘
      │
      ▼
     END
```

---

## 5. SESSION HISTORY & CONTEXT MANAGEMENT

### Two Levels of Session Storage:

#### Level 1: Chat-Server (UI Sessions)
**File:** `chat-server/session_manager.py`
- **Stores:** User messages and assistant responses
- **Purpose:** Display in the UI, maintain conversation view
- **Scope:** All messages from all services

#### Level 2: Conversational-Workflow (LLM Context)
**File:** `conversational-workflow/workflow.py`
- **Stores:** Conversation history for OpenAI context
- **Purpose:** Provide context to LLM so it remembers previous messages
- **Scope:** Only messages processed by this workflow

### Example:

```
User: "What is Faust?"
AI: "Faust is a stream processing library for Python..."

User: "What are its benefits?"
AI: "The main benefits of using Faust include..."
     ↑ AI remembers we're talking about Faust because of session_histories
```

**Code:**

```python
# conversational-workflow/workflow.py

self.session_histories: Dict[str, List[Dict[str, str]]] = {}

# When calling LLM, include history:
for msg in state["chat_history"]:
    if msg["role"] == "user":
        messages.append(HumanMessage(content=msg["content"]))
    else:
        messages.append(AIMessage(content=msg["content"]))
```

---

## 6. SYSTEM COMPONENTS SUMMARY

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| **chat-server** | FastAPI + WebSocket | 8000 | User interface, session management, Kafka producer/consumer |
| **workflow-orchestrator** | Faust + LangGraph | 6066 (web) | Stream processing, supervisor agent, orchestration |
| **conversational-workflow** | FastAPI + LangGraph + OpenAI | 8001 | LLM integration, conversation logic |
| **Kafka** | Apache Kafka | 9092 | Message queue, async communication |
| **Zookeeper** | Apache Zookeeper | 2181 | Kafka cluster management |
| **Kafka UI** | UI for Apache Kafka | 8080 | Monitor Kafka topics, messages, consumers |

---

## 7. KEY ARCHITECTURAL DECISIONS

### Why Kafka?
- **Asynchronous processing**: User doesn't wait for LLM response synchronously
- **Scalability**: Can add more Faust workers
- **Reliability**: Messages persist in Kafka if services restart
- **Decoupling**: Services don't need to know about each other

### Why Faust?
- **Stream processing**: Native Python library for Kafka streams
- **Easy to use**: Pythonic API, similar to Flask/FastAPI decorators
- **Built-in features**: State stores, tables, windowing for complex stream processing

### Why LangGraph (Twice)?
- **Supervisor Agent**: Orchestrates which service to call, handles routing
- **Conversational Workflow**: Manages LLM conversation flow, context, history
- **Separation of Concerns**: Orchestration logic separate from conversation logic

### Why Two Session Stores?
- **chat-server**: Full conversation for UI display
- **conversational-workflow**: LLM-specific context for OpenAI API
- **Reason**: Separation allows conversational-workflow to be stateless and horizontally scalable

---

## 8. MESSAGE TRACING EXAMPLE

Let's trace the message "What is Faust?" through the entire system:

```
Time | Component                  | Action
-----|----------------------------|------------------------------------------
T1   | Browser                    | User types "What is Faust?" and clicks send
T2   | chat-server (WebSocket)    | Receives message, stores as "user" role
T3   | chat-server (kafka_handler)| Publishes to Kafka topic "chat-requests"
T4   | Kafka                      | Stores message in partition
T5   | Faust Worker              | Consumes message from "chat-requests"
T6   | supervisor_agent          | LangGraph receives request
T7   | supervisor_agent          | HTTP POST to conversational-workflow:8001/chat
T8   | conversational-workflow   | Receives HTTP request
T9   | ConversationalWorkflow    | LangGraph prepares messages with history
T10  | ConversationalWorkflow    | Calls self.llm.invoke(messages)
T11  | OpenAI API                | Processes request, generates response
T12  | ConversationalWorkflow    | Receives "Faust is a stream processing..."
T13  | ConversationalWorkflow    | Stores in session_histories
T14  | conversational-workflow   | Returns HTTP response to supervisor
T15  | supervisor_agent          | Receives response, updates state
T16  | Faust Worker              | Creates ChatResponse object
T17  | Faust Worker              | Publishes to Kafka topic "chat-responses"
T18  | Kafka                      | Stores response in partition
T19  | chat-server (kafka_handler)| Consumer receives response from Kafka
T20  | chat-server               | Stores response in session_manager
T21  | chat-server               | Sends WebSocket message to browser
T22  | Browser                    | Displays "Faust is a stream processing..."
```

**Total Time:** Typically 1-3 seconds (mostly OpenAI API latency at T10-T11)

---

## Conclusion

This architecture demonstrates a **production-ready microservices pattern** for AI applications:

✅ **Scalable**: Each component can scale independently
✅ **Resilient**: Kafka ensures message delivery even if services restart
✅ **Maintainable**: Clear separation of concerns
✅ **Extensible**: Easy to add new agents or workflows
✅ **Observable**: Kafka UI for monitoring, logs at each step

The **OpenAI LLM call** happens in `conversational-workflow/workflow.py:82` via `self.llm.invoke(messages)`.
