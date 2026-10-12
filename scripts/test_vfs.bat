@echo off
cd /d "%~dp0.."
if not exist runtime mkdir runtime
for %%N in (minimal multiple deep) do (
    copy /Y examples\%%N.xml runtime\%%N.xml >nul
    call run.bat --headless --vfs runtime\%%N.xml --startup examples\stage3.txt
)
call run.bat --headless --vfs examples\invalid.xml --startup examples\stage3.txt
pause
