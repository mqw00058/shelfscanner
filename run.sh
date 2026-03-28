#!/bin/bash
cd /home/jiy/Projects/shelf-scanner

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Kill any existing server on port 8000
fuser -k 8000/tcp 2>/dev/null

echo "Starting Shelf Scanner server at http://localhost:8000"
/home/jiy/miniconda3/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
