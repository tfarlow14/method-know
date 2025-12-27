#!/usr/bin/env bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env.local if it exists
if [ -f .env.local ]; then
    echo "Loading environment variables from .env.local"
    set -a  # Automatically export all variables
    source .env.local
    set +a  # Stop automatically exporting
fi

# Check for required AWS profile (local development only)
if [ -z "$AWS_PROFILE" ]; then
    echo "Error: AWS_PROFILE is not set"
    echo "Please set AWS_PROFILE in .env.local or export it before running this script"
    echo "Example: export AWS_PROFILE=your-profile-name"
    exit 1
fi

echo "Using AWS profile: $AWS_PROFILE"

# Check for required TABLE_PREFIX
if [ -z "$TABLE_PREFIX" ]; then
    echo "Error: TABLE_PREFIX is not set"
    echo "Please set TABLE_PREFIX in .env.local or export it before running this script"
    echo "Example: export TABLE_PREFIX=knowledge-hub-api"
    exit 1
fi

# Set environment variables (only if not already set)
export CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:5173,http://localhost:4173}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key}
export AWS_REGION=${AWS_REGION:-us-east-1}

# Optional: Uncomment for DynamoDB Local instead of real AWS
# export AWS_ENDPOINT_URL=http://localhost:8000

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
