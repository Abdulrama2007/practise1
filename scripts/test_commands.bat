@echo off
cd /d "%~dp0.."
if not exist runtime mkdir runtime
copy /Y examples\deep.xml runtime\commands.xml >nul
call run.bat --headless --vfs runtime\commands.xml --startup examples\stage4.txt
call run.bat --headless --vfs runtime\commands.xml --startup examples\stage5.txt
copy /Y examples\deep.xml runtime\all.xml >nul
call run.bat --headless --vfs runtime\all.xml --startup examples\all_commands.txt
pause
