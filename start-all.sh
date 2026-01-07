#!/bin/bash

echo "=========================================="
echo "Starting Agentic Chat Workflow System"
echo "=========================================="

# Start Kafka
echo ""
echo "1. Starting Kafka infrastructure..."
docker-compose up -d

echo "Waiting for Kafka to be ready (30 seconds)..."
sleep 30

# Check if Kafka is running
if docker-compose ps | grep -q kafka.*Up; then
    echo "✓ Kafka is running"
else
    echo "✗ Kafka failed to start. Please check docker-compose logs"
    exit 1
fi

echo ""
echo "=========================================="
echo "Kafka UI available at: http://localhost:8080"
echo "=========================================="

echo ""
echo "Now start the following services in separate terminals:"
echo ""
echo "Terminal 1 - Conversational Workflow:"
echo "  cd conversational-workflow"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 - Workflow Orchestrator:"
echo "  cd workflow-orchestrator"
echo "  source venv/bin/activate"
echo "  python orchestrator.py"
echo ""
echo "Terminal 3 - Chat Server:"
echo "  cd chat-server"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open http://localhost:8000 in your browser"
echo "=========================================="
