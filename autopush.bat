@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        Tastio 2.0 - Automated Git Stage, Commit ^& Push
echo ========================================================

set "COMMIT_MSG=%~1"
if "%COMMIT_MSG%"=="" (
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%c-%%a-%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a:%%b
    set "COMMIT_MSG=auto-sync: !mydate! !mytime!"
)

echo [1/3] Staging all project changes...
git add -A

echo [2/3] Committing changes...
git commit -m "%COMMIT_MSG%"

echo [3/3] Pushing to GitHub (origin main)...
git push origin main

echo ========================================================
echo Auto-push complete!
echo ========================================================
pause
