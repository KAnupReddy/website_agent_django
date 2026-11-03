@echo off
REM ==================================================================
REM  AutoBiz AI (Django) - one-click start
REM  Creates the virtualenv on first run, installs requirements,
REM  creates the MySQL database if needed, applies migrations and
REM  starts the dev server at http://127.0.0.1:8000
REM ==================================================================
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

if not exist ".venv\Scripts\python.exe" (
    echo [1/5] Creating virtual environment...
    python -m venv .venv || (echo Python 3.12+ is required on PATH. & pause & exit /b 1)
) else (
    echo [1/5] Virtual environment found.
)

echo [2/5] Installing requirements...
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || (echo pip install failed. & pause & exit /b 1)

if not exist ".env" (
    echo        No .env found - copying .env.example to .env
    copy /y ".env.example" ".env" >nul
)

echo [3/5] Ensuring database exists...
".venv\Scripts\python.exe" manage.py ensure_database || (echo Could not reach the database. Is MySQL running in XAMPP? & pause & exit /b 1)

echo [4/5] Applying migrations...
".venv\Scripts\python.exe" manage.py migrate --noinput || (pause & exit /b 1)

echo [5/5] Starting server at http://127.0.0.1:8000  (Ctrl+C to stop)
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

endlocal
