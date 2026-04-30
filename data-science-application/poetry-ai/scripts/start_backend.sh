#!/bin/bash
# Start the backend server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/.."
VENV_DIR="$PROJECT_DIR/../.datascienceapp"

cd "$PROJECT_DIR"

# Activate virtual environment if it exists (venv lives one level above poetry-ai/)
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Start the server
export PYTHONPATH="$(pwd)/src"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
