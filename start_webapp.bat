@echo off
REM PDF to Markdown Converter Web App Startup Script for Windows

echo 🚀 Starting PDF to Markdown Converter Web App...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is required but not installed.
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 📦 Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo 🔧 Starting backend server...
start "Backend Server" cmd /k "cd backend && python main.py"

echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 🎨 Starting frontend development server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ✅ Web app is starting up!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo.
echo Press any key to exit...
pause >nul
