#!/bin/bash

echo "Starting Conversational Workflow Service..."
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Copy .env.example to .env and add your OPENAI_API_KEY"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Run setup first."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Run the application
python app.py
