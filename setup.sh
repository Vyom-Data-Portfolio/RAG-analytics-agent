#!/bin/bash
# RAG Analytics Agent - Mac/Linux Setup Script
# Run with: bash setup.sh

echo "========================================"
echo "RAG Analytics Agent - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo "Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. cp .env.example .env"
echo "2. Add your ANTHROPIC_API_KEY to .env"
echo "3. python embed_knowledge_base.py"
echo "4. python agent_with_rag.py"
echo ""
echo "For detailed instructions, see SETUP_GUIDE.md"
echo ""
