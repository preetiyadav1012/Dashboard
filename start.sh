#!/bin/bash
# Quick start script for Unix/Linux/macOS

echo "🚀 Starting Claims Management Dashboard..."
echo ""

# Start backend
echo "📦 Starting Backend Server..."
cd backend
pip install -r requirements.txt
python app.py &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo ""

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "💻 Starting Frontend Server..."
cd ../frontend
npm install
npm start &
FRONTEND_PID=$!

echo "Frontend started with PID: $FRONTEND_PID"
echo ""

echo "✅ Dashboard is starting!"
echo "🌐 Open your browser at: http://localhost:3000"
echo ""
echo "To stop the servers, press Ctrl+C or run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"

wait
