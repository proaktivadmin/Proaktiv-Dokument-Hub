@echo off
echo Sending signature emails...
powershell -ExecutionPolicy Bypass -File "backend\scripts\Send-SignatureEmails.ps1" %*
pause
