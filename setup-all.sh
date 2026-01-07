#!/bin/bash

echo "=========================================="
echo "Setting up Agentic Chat Workflow System"
echo "=========================================="

# Function to setup a project
setup_project() {
    local project_name=$1
    local project_dir=$2

    echo ""
    echo "Setting up $project_name..."
    cd "$project_dir"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Deactivate
    deactivate

    echo "✓ $project_name setup complete"

    cd ..
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker."
    exit 1
fi

# Setup each project
setup_project "Conversational Workflow" "conversational-workflow"
setup_project "Workflow Orchestrator" "workflow-orchestrator"
setup_project "Chat Server" "chat-server"

# Setup environment file for conversational-workflow
echo ""
echo "Setting up environment file..."
if [ ! -f "conversational-workflow/.env" ]; then
    cp conversational-workflow/.env.example conversational-workflow/.env
    echo "⚠ Please edit conversational-workflow/.env and add your OPENAI_API_KEY"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit conversational-workflow/.env and add your OPENAI_API_KEY"
echo "2. Run ./start-all.sh to start Kafka"
echo "3. Follow the instructions to start each service"
echo ""
echo "For detailed instructions, see README.md"
echo "=========================================="
