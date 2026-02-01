@echo off
REM RAG Analytics Agent - Windows Setup Script
REM Run this after extracting the project

echo ========================================
echo RAG Analytics Agent - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your ANTHROPIC_API_KEY to .env
echo 3. Run: python embed_knowledge_base.py
echo 4. Run: python agent_with_rag.py
echo.
echo For detailed instructions, see SETUP_GUIDE.md
echo.
pause
