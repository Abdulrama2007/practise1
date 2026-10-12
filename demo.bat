@echo off
cd /d "%~dp0"
if not exist runtime mkdir runtime
copy /Y examples\deep.xml runtime\demo.xml >nul
call run.bat --vfs runtime\demo.xml --startup examples\demo.txt
if errorlevel 1 pause
