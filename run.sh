#!/bin/bash

# Kill background processes on exit
trap 'kill 0' EXIT

cd "$(dirname "$0")"

# Backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &

# Frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &

wait
