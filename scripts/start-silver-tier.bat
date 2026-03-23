@echo off
REM AI Employee - Silver Tier Quick Start Script
REM Starts all watchers and orchestrator for Silver Tier

echo ============================================
echo AI Employee - Silver Tier Startup
echo ============================================
echo.

cd /d "%~dp0"

REM Check if vault exists
if not exist "..\AI_Employee_Vault" (
    echo ERROR: AI_Employee_Vault not found!
    pause
    exit /b 1
)

REM Check if token.json exists for Gmail
if not exist "token.json" (
    echo WARNING: Gmail token.json not found!
    echo Please run authentication first:
    echo   python gmail_authenticate.py
    echo.
    pause
)

echo Starting File System Watcher...
start "AI Employee - File Watcher" cmd /k "python filesystem_watcher.py ../AI_Employee_Vault"

timeout /t 2 /nobreak >nul

echo Starting Gmail Watcher...
start "AI Employee - Gmail Watcher" cmd /k "python gmail_watcher.py ../AI_Employee_Vault"

timeout /t 2 /nobreak >nul

echo Starting LinkedIn Watcher...
start "AI Employee - LinkedIn Watcher" cmd /k "python linkedin_watcher.py ../AI_Employee_Vault"

timeout /t 2 /nobreak >nul

echo Starting Orchestrator...
start "AI Employee - Orchestrator" cmd /k "python orchestrator.py ../AI_Employee_Vault"

echo.
echo ============================================
echo All processes started!
echo.
echo Running Services:
echo   - File System Watcher (monitoring Inbox)
echo   - Gmail Watcher (monitoring emails)
echo   - LinkedIn Watcher (auto-posting)
echo   - Orchestrator (processing tasks)
echo.
echo To stop: Close the terminal windows
echo.
echo To test Gmail:
echo   1. Send yourself an email with subject "Test"
echo   2. Wait for Gmail Watcher to detect it
echo.
echo To test LinkedIn:
echo   1. Run: python linkedin_watcher.py ../AI_Employee_Vault
echo   2. Approve a post in Pending_Approval folder
echo ============================================
echo.

pause
