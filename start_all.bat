@echo off
echo ========================================================
echo        Tastio 2.0 - Starting Backend and Mobile App
echo ========================================================

echo [1/2] Checking Python Backend on http://localhost:5000 ...
netstat -ano | findstr :5000 >nul
if %ERRORLEVEL% EQU 0 (
    echo Python Backend is already running on port 5000.
) else (
    echo Starting Python Backend in new window...
    start "Tastio Backend API" cmd /k "cd /d %~dp0backend && ..\.venv\Scripts\python.exe app.py"
    timeout /t 4 >nul
)

echo [2/2] Starting Expo Development Server...
cd /d "%~dp0mobile-app"
call npx.cmd expo start
