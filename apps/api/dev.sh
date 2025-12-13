#!/usr/bin/env bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Use absolute path to venv python
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Check if requirements are installed
if ! "$VENV_PYTHON" -c "import fastapi" 2>/dev/null || ! "$VENV_PYTHON" -c "import jwt" 2>/dev/null; then
    echo "Installing Python dependencies..."
    "$VENV_PYTHON" -m pip install -r requirements.txt
fi

# Run uvicorn using the venv python
"$VENV_PYTHON" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
