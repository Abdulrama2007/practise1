@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m src.main %*
) else (
    python -m src.main %*
)
exit /b %errorlevel%
