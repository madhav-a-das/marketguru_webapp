@echo off
echo Starting MarketGuru - Enhanced Product Detection System
echo.
echo Starting backend...
start "Backend" cmd /k "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo System started!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo Press any key to exit this window...
pause > nul 