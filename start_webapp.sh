#!/bin/bash

# PDF to Markdown Converter Web App Startup Script

echo "🚀 Starting PDF to Markdown Converter Web App..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Check if curl is installed (for health checks)
if ! command -v curl &> /dev/null; then
    echo "⚠️  curl is not installed. Health checks will be skipped."
    SKIP_HEALTH_CHECKS=true
else
    SKIP_HEALTH_CHECKS=false
fi

# Function to check if port is in use
check_port() {
    local port=$1
    local process_name=$2
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pid" ]; then
        echo "⚠️  Port $port is in use by process $pid ($process_name)"
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local process_name=$2
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pid" ]; then
        echo "🛑 Killing existing $process_name process (PID: $pid) on port $port..."
        kill -TERM $pid 2>/dev/null
        
        # Wait a moment for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "🔨 Force killing $process_name process (PID: $pid)..."
            kill -KILL $pid 2>/dev/null
        fi
        
        # Verify port is free
        sleep 1
        if check_port $port "$process_name"; then
            echo "❌ Failed to free port $port"
            exit 1
        else
            echo "✅ Port $port is now free"
        fi
    fi
}

# Check and clean up existing processes
echo "🔍 Checking for existing processes..."

# Check backend port (8000)
if check_port 8000 "uvicorn/FastAPI"; then
    kill_port 8000 "uvicorn/FastAPI"
fi

# Check frontend port (3000)
if check_port 3000 "React dev server"; then
    kill_port 3000 "React dev server"
fi

# Additional cleanup for any remaining Python/Node processes related to our app
echo "🧹 Cleaning up any remaining app processes..."

# Kill any remaining python processes running main.py
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Cleaned up Python main.py processes"

# Kill any remaining react-scripts processes
pkill -f "react-scripts start" 2>/dev/null && echo "✅ Cleaned up React dev server processes"

# Wait a moment for cleanup to complete
sleep 2

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo "🔧 Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
if [ "$SKIP_HEALTH_CHECKS" = true ]; then
    echo "⏳ Waiting 10 seconds for backend to start (health checks disabled)..."
    sleep 10
    echo "✅ Backend server should be ready!"
else
    # Wait for backend to be ready
    for i in {1..10}; do
        if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
            echo "✅ Backend server is ready!"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Backend server failed to start properly"
            cleanup
            exit 1
        fi
        echo "⏳ Waiting for backend... ($i/10)"
        sleep 2
    done
fi

echo "🎨 Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for frontend to start..."
if [ "$SKIP_HEALTH_CHECKS" = true ]; then
    echo "⏳ Waiting 15 seconds for frontend to start (health checks disabled)..."
    sleep 15
    echo "✅ Frontend server should be ready!"
else
    # Wait for frontend to be ready
    for i in {1..15}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ Frontend server is ready!"
            break
        fi
        if [ $i -eq 15 ]; then
            echo "⚠️  Frontend server may still be starting..."
            break
        fi
        echo "⏳ Waiting for frontend... ($i/15)"
        sleep 2
    done
fi

echo ""
echo "✅ Web app is starting up!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    
    # Gracefully stop backend
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🛑 Stopping backend server (PID: $BACKEND_PID)..."
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "🔨 Force killing backend server..."
            kill -KILL $BACKEND_PID 2>/dev/null
        fi
    fi
    
    # Gracefully stop frontend
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🛑 Stopping frontend server (PID: $FRONTEND_PID)..."
        kill -TERM $FRONTEND_PID 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "🔨 Force killing frontend server..."
            kill -KILL $FRONTEND_PID 2>/dev/null
        fi
    fi
    
    # Additional cleanup for any remaining processes
    echo "🧹 Final cleanup..."
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "react-scripts start" 2>/dev/null
    
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
