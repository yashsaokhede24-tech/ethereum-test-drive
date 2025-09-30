@echo off
echo 🚀 Starting Quantum-Safe Blockchain Guardrail...

echo.
echo 📦 Starting Python Backend...
start "Backend API" cmd /k "cd backend && python app.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Starting React Frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak > nul

echo.
echo 🎯 Starting Main Application...
start "Main App" cmd /k "node src/index.js"

echo.
echo 🎉 All services started!
echo.
echo 📊 Dashboard: http://localhost:3000
echo 🔧 Backend API: http://localhost:5000
echo.
echo Press any key to close this window...
pause > nul
