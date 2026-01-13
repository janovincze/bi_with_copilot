#!/bin/bash
#
# Copilot Analytics - Setup Script (Unix/macOS/Linux)
# This script sets up the Python environment and builds the dbt project.
#

set -e  # Exit on error

echo "=============================================="
echo "   Copilot Analytics - Setup Script"
echo "=============================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Find compatible Python version (3.9-3.13, not 3.14+ due to dbt compatibility)
PYTHON_CMD=""
for cmd in python3.13 python3.12 python3.11 python3.10 python3.9; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

# Check Homebrew Python on macOS
if [ -z "$PYTHON_CMD" ] && [ -f "/opt/homebrew/opt/python@3.13/bin/python3.13" ]; then
    PYTHON_CMD="/opt/homebrew/opt/python@3.13/bin/python3.13"
elif [ -z "$PYTHON_CMD" ] && [ -f "/opt/homebrew/opt/python@3.12/bin/python3.12" ]; then
    PYTHON_CMD="/opt/homebrew/opt/python@3.12/bin/python3.12"
fi

# Fallback to python3 but check version
if [ -z "$PYTHON_CMD" ]; then
    if command -v python3 &> /dev/null; then
        PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
        PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
        if [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 9 ] && [ "$PY_MINOR" -le 13 ]; then
            PYTHON_CMD="python3"
        else
            echo "Error: Python $PY_VERSION found, but dbt requires Python 3.9-3.13"
            echo "Python 3.14+ has compatibility issues with dbt."
            echo "Please install Python 3.13: brew install python@3.13"
            exit 1
        fi
    else
        echo "Error: Python 3 is required but not installed."
        echo "Please install Python 3.9-3.13 from https://python.org"
        exit 1
    fi
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "  Python: $PYTHON_VERSION ($PYTHON_CMD)"

# Check Node.js (for copilot-api)
if ! command -v npx &> /dev/null; then
    echo "Warning: Node.js/npm not found."
    echo "You'll need it to run copilot-api."
    echo "Install from https://nodejs.org"
else
    echo "  Node.js: OK"
fi

echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Build dbt project
echo ""
echo "Building dbt project..."
cd dbt_project

# Install dbt dependencies (if any)
if [ -f "packages.yml" ]; then
    dbt deps
fi

# Load seed data
echo "  Loading seed data..."
dbt seed --quiet

# Build models
echo "  Building models..."
dbt build --quiet

cd ..

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "Created .env file from template."
fi

echo ""
echo "=============================================="
echo "   Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Authenticate with GitHub Copilot (one-time):"
echo "   npx copilot-api@latest auth"
echo ""
echo "2. Start the Copilot API server:"
echo "   npx copilot-api@latest start --rate-limit 10"
echo ""
echo "3. In a NEW terminal, start the dashboard:"
echo "   source venv/bin/activate"
echo "   cd ai_dashboard"
echo "   streamlit run app_streamlit.py  # Opens at http://localhost:8501"
echo ""
echo "Quick commands with Make:"
echo "   make copilot-auth   # Authenticate Copilot"
echo "   make copilot-start  # Start Copilot API"
echo "   make run-streamlit  # Start Streamlit app"
echo "   make run-flask      # Alternative: Flask app (http://localhost:8084)"
echo ""
