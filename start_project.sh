#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "🚀 Starting Smart Study Planner..."

# 1. Start Backend in the background
echo "📅 Starting Flask Backend (Port 5000)..."
cd api
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python index.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 2. Start Frontend Static Server
echo "🌐 Starting Frontend Server (Port 8000)..."
cd frontend
python3 -m http.server 8000 > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "------------------------------------------------"
echo "✅ SUCCESS! The app is now running."
echo "👉 Frontend: http://localhost:8000"
echo "👉 Backend API: http://localhost:5000"
echo "------------------------------------------------"
echo "Press Ctrl+C to stop both servers."

# Trap Ctrl+C to kill both background processes
trap "kill $BACKEND_PID $FRONTEND_PID; echo '🛑 Servers stopped.'; exit" INT

# Wait for background processes
wait
