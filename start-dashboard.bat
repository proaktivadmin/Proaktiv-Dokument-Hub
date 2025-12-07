@echo off
echo ======================================
echo   Starting HTML Hub Dashboard
echo ======================================
echo.

:: Start the backend server in a new window
echo Starting backend server...
start "HTML Hub Backend" cmd /k "npm run dev"

:: Wait a moment for backend to initialize
timeout /t 2 /nobreak > nul

:: Start the frontend Vite dev server
echo Starting frontend...
start "HTML Hub Frontend" cmd /k "cd client && npm run dev"

echo.
echo ======================================
echo   Dashboard is starting up!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:3001
echo ======================================
echo.
echo Press any key to close this window...
pause > nul
