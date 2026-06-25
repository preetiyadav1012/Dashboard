@echo off
REM Quick start script for Windows

echo 🚀 Starting Claims Management Dashboard...
echo.

REM Create two terminals - one for backend, one for frontend

echo 📦 Backend will start in a new window...
start cmd /k "cd backend && pip install -r requirements.txt && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak

echo 💻 Frontend will start in a new window...
start cmd /k "cd frontend && npm install && npm start"

echo.
echo ✅ Dashboard is starting!
echo 🌐 Frontend will open at: http://localhost:3000
echo Backend API running at: http://localhost:5000
echo.
echo Close the command windows to stop the servers.

pause
