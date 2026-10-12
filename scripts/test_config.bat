@echo off
cd /d "%~dp0.."
call run.bat --headless --startup examples\stage2.txt
call run.bat --headless --vfs examples\minimal.xml --startup examples\stage2.txt
call run.bat --headless --startup examples\missing.txt
pause
