@echo off
echo 🚀 Starting REAL Quantum-Safe Blockchain Guardrail Model...
echo.

echo 📦 Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python working_backend.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Opening Real Dashboard...
start "" "real-dashboard.html"

echo.
echo ✅ REAL WORKING MODEL STARTED!
echo.
echo 📊 Dashboard: real-dashboard.html
echo 🔧 Backend API: http://localhost:5000
echo.
echo 🎯 Features:
echo   • Process REAL transactions
echo   • Live anomaly detection
echo   • PQC signature upgrades
echo   • Real-time statistics
echo   • Auto-processing mode
echo.
echo Press any key to close this window...
pause > nul
