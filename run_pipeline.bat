@echo off
REM ==================================================================
REM  Run the AutoBiz AI pipeline from the command line.
REM    run_pipeline.bat        -> all pending businesses (no website)
REM    run_pipeline.bat 5      -> only business #5
REM ==================================================================
setlocal
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

if not exist ".venv\Scripts\python.exe" (
    echo Run run.bat once first to set up the project.
    pause & exit /b 1
)

if "%~1"=="" (
    ".venv\Scripts\python.exe" manage.py agent_run
) else (
    ".venv\Scripts\python.exe" manage.py agent_run --id %1
)

endlocal
