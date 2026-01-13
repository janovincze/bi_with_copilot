@echo off
REM
REM Copilot Analytics - Setup Script (Windows)
REM This script sets up the Python environment and builds the dbt project.
REM

echo ==============================================
echo    Copilot Analytics - Setup Script
echo ==============================================
echo.

REM Check Python version (requires 3.9-3.13, not 3.14+ due to dbt compatibility)
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not installed.
    echo Please install Python 3.9-3.13 from https://python.org
    echo Note: Python 3.14+ has compatibility issues with dbt.
    exit /b 1
)

REM Get Python version and check compatibility
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJOR=%%a
    set PYMINOR=%%b
)

if %PYMINOR% GEQ 14 (
    echo Error: Python %PYVER% found, but dbt requires Python 3.9-3.13
    echo Python 3.14+ has compatibility issues with dbt.
    echo Please install Python 3.13 from https://python.org
    exit /b 1
)

if %PYMINOR% LSS 9 (
    echo Error: Python %PYVER% found, but dbt requires Python 3.9-3.13
    echo Please install Python 3.13 from https://python.org
    exit /b 1
)

echo   Python: %PYVER% (OK)

REM Check Node.js
npx --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Node.js/npm not found.
    echo You'll need it to run copilot-api.
    echo Install from https://nodejs.org
) else (
    echo   Node.js: OK
)

echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt --quiet

REM Build dbt project
echo.
echo Building dbt project...
cd dbt_project

REM Load seed data
echo   Loading seed data...
dbt seed --quiet

REM Build models
echo   Building models...
dbt build --quiet

cd ..

REM Copy environment file
if not exist .env (
    copy .env.example .env
    echo.
    echo Created .env file from template.
)

echo.
echo ==============================================
echo    Setup Complete!
echo ==============================================
echo.
echo Next steps:
echo.
echo 1. Authenticate with GitHub Copilot (one-time):
echo    npx copilot-api@latest auth
echo.
echo 2. Start the Copilot API server:
echo    npx copilot-api@latest start --rate-limit 10
echo.
echo 3. In a NEW command prompt, start the dashboard:
echo    venv\Scripts\activate
echo    cd ai_dashboard
echo    streamlit run app_streamlit.py
echo.
echo Opens at http://localhost:8501
echo.
