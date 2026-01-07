# Testing Guide

Step-by-step guide to verify all components of the Agentic Chat Workflow System are working correctly.

## Pre-Testing Checklist

- [ ] Docker and Docker Compose installed
- [ ] Python 3.9+ installed
- [ ] All three projects have virtual environments set up
- [ ] OpenAI API key configured in `conversational-workflow/.env`

## Test 1: Kafka Infrastructure

### Start Kafka

```bash
docker-compose up -d
```

### Verify Kafka is Running

```bash
# Check containers are up
docker-compose ps

# Expected output:
# zookeeper ... Up
# kafka ... Up
# kafka-ui ... Up
```

### Test Kafka UI

1. Open http://localhost:8080 in browser
2. You should see the Kafka UI dashboard
3. Check for topics (may be empty initially)

**Expected Result:** Kafka UI loads successfully

## Test 2: Conversational Workflow Service

### Start the Service

```bash
cd conversational-workflow
source venv/bin/activate
python app.py
```

### Test Health Endpoint

In a new terminal:

```bash
curl http://localhost:8001/health
```

**Expected Output:**
```json
{"status":"healthy","service":"conversational-workflow"}
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Hello, how are you?"
  }'
```

**Expected Output:**
```json
{
  "session_id": "test-123",
  "response": "I'm doing well, thank you for asking! How can I help you today?"
}
```

**Success Criteria:**
- Service starts without errors
- Health check returns 200
- Chat endpoint returns AI response
- No OpenAI API errors

## Test 3: Workflow Orchestrator

### Start the Orchestrator

In a new terminal:

```bash
cd workflow-orchestrator
source venv/bin/activate
python orchestrator.py
```

**Expected Log Output:**
```
Starting Workflow Orchestrator...
Kafka producer connected
Kafka consumer connected to topic: chat-requests
Workflow Orchestrator started successfully
Waiting for requests...
```

**Success Criteria:**
- Connects to Kafka successfully
- No connection errors
- Subscribes to chat-requests topic

## Test 4: Chat Server

### Start Chat Server

In a new terminal:

```bash
cd chat-server
source venv/bin/activate
python app.py
```

**Expected Log Output:**
```
Kafka producer connected
Kafka consumer thread started
Chat server started successfully
```

### Test Web UI

1. Open http://localhost:8000 in browser
2. Click "New Chat" button
3. Verify:
   - Status shows "Connected" (green)
   - Message input is enabled
   - Session appears in sidebar

**Success Criteria:**
- UI loads without errors
- WebSocket connects successfully
- New session created

## Test 5: End-to-End Message Flow

With all three services running:

### Send a Test Message

1. In the chat UI (http://localhost:8000)
2. Type: "Tell me a fun fact about Python"
3. Press Enter or click Send

### Monitor Each Service

**Chat Server logs should show:**
```
Sent message to Kafka for session <session_id>
```

**Orchestrator logs should show:**
```
Received request for session <session_id>
Calling conversational workflow for session <session_id>
Successfully processed request for session <session_id>
```

**Conversational Workflow logs should show:**
```
Received chat request for session <session_id>
Calling OpenAI LLM for session <session_id>
```

**Chat UI should show:**
- Your message appears on the right (blue)
- AI response appears on the left (green)
- Response arrives within 2-5 seconds

**Success Criteria:**
- Message flows through all services
- Response appears in UI
- All logs show successful processing

## Test 6: Kafka Topics

### Check Topics in Kafka UI

1. Open http://localhost:8080
2. Click on "Topics"
3. Verify two topics exist:
   - `chat-requests`
   - `chat-responses`

### View Messages

1. Click on `chat-requests` topic
2. Click "Messages" tab
3. You should see your test messages

**Success Criteria:**
- Both topics created automatically
- Messages visible in Kafka UI

## Test 7: Session Management

### Create Multiple Sessions

1. In chat UI, click "New Chat"
2. Send a message: "My name is Alice"
3. Click "New Chat" again (new session)
4. Send a message: "My name is Bob"
5. Click on the first session in sidebar
6. Send: "What's my name?"

**Expected:** AI responds "Alice" (context from first session)

7. Click on second session
8. Send: "What's my name?"

**Expected:** AI responds "Bob" (context from second session)

**Success Criteria:**
- Multiple sessions work independently
- Conversation history maintained per session
- Can switch between sessions

## Test 8: Error Handling

### Test with Orchestrator Stopped

1. Stop the orchestrator (Ctrl+C)
2. Send a message in chat UI
3. Wait 30 seconds

**Expected:** Message sent to Kafka but no response (orchestrator down)

4. Restart orchestrator
5. Send another message

**Expected:** New message should get response

**Success Criteria:**
- System handles missing services gracefully
- Recovery works when service restarts

## Test 9: Load Test (Optional)

### Send Multiple Messages Quickly

1. Create a new session
2. Send 10 messages rapidly:
   - "Count to 10"
   - "What is 2+2?"
   - "Tell me a joke"
   - etc.

**Expected:**
- All messages processed in order
- All responses received
- No crashes or hangs

**Success Criteria:**
- System handles rapid messages
- Responses arrive for all messages

## Test 10: Cleanup and Restart

### Stop All Services

1. Stop Chat Server (Ctrl+C)
2. Stop Orchestrator (Ctrl+C)
3. Stop Conversational Workflow (Ctrl+C)
4. Stop Kafka: `docker-compose down`

### Restart Everything

```bash
# Start Kafka
docker-compose up -d
sleep 30

# Terminal 1
cd conversational-workflow && source venv/bin/activate && python app.py

# Terminal 2
cd workflow-orchestrator && source venv/bin/activate && python orchestrator.py

# Terminal 3
cd chat-server && source venv/bin/activate && python app.py
```

### Verify

- Open http://localhost:8000
- Create new session
- Send test message
- Verify response received

**Success Criteria:**
- Clean restart works
- All services reconnect
- System functional after restart

## Common Issues and Solutions

### Issue: Kafka won't start
```bash
# Solution: Clean Kafka data
docker-compose down -v
docker-compose up -d
```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :8000  # or 8001, 9092

# Kill process
kill -9 <PID>
```

### Issue: OpenAI API error
- Check API key in .env file
- Verify OpenAI account has credits
- Check internet connection

### Issue: WebSocket won't connect
- Verify Chat Server is running on port 8000
- Check browser console for errors
- Try different browser

### Issue: No response from AI
- Check all three services are running
- Verify Kafka topics exist in Kafka UI
- Check logs in each service terminal

## Performance Benchmarks

**Expected Response Times:**
- Message send to UI update: 2-5 seconds
- Kafka message propagation: < 100ms
- OpenAI API call: 1-3 seconds
- End-to-end latency: 2-5 seconds

**Resource Usage:**
- Chat Server: ~50MB RAM
- Orchestrator: ~100MB RAM
- Conversational Workflow: ~150MB RAM
- Kafka: ~512MB RAM

## Success Criteria Summary

All tests passed means:
- ✅ Kafka infrastructure running
- ✅ All three services start without errors
- ✅ End-to-end message flow works
- ✅ WebSocket real-time updates work
- ✅ Session management works
- ✅ OpenAI integration works
- ✅ Error recovery works
- ✅ System can restart cleanly

## Next Steps After Testing

Once all tests pass:
1. Review logs for any warnings
2. Test with different types of messages
3. Explore the code in each project
4. Customize the system prompt in workflow.py
5. Add your own features!

For production deployment, see README.md "Next Steps" section.
