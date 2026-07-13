#!/bin/bash

# Exit on error
set -e

# Project root
ROOT="/Users/hassam/Documents/my_data/internship/task1"

echo "Starting Task AI development environment..."

# Activate Python virtual environment
source "$ROOT/venv/bin/activate"

# Start FastAPI backend
echo "Starting FastAPI backend..."
(
    cd "$ROOT/agent"
    uvicorn main:app --host 0.0.0.0 --port 8000
) &

BACKEND_PID=$!

# Start Next.js frontend
echo "Starting Next.js frontend..."
(
    cd "$ROOT/frontend"
    npm run dev
) &

FRONTEND_PID=$!

echo ""
echo "Frontend: http://localhost:3000"
echo "Backend : http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both services."

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait
    echo "Done."
}

trap cleanup INT TERM

# Wait for both processes
wait