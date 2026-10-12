@echo off
cd /d "%~dp0"
call run.bat %*
if errorlevel 1 pause
