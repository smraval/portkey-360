#!/bin/bash

# Portkey360 Startup Script
echo "🚀 Starting Portkey360..."

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Portkey360 is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait 