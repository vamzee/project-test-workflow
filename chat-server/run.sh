#!/bin/bash

echo "Starting Chat Server..."
echo "Make sure Kafka is running first (docker-compose up -d)"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Run setup first."
    exit 1
fi

# Run the application
python app.py
