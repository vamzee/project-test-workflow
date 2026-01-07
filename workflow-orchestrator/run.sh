#!/bin/bash

echo "Starting Workflow Orchestrator..."
echo "Make sure Kafka and Conversational Workflow are running first."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Run setup first."
    exit 1
fi

# Run the application
python orchestrator.py
