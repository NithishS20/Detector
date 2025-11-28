@echo off
REM start_both_server.bat
REM Wrapper to start the Detector application

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "start_servers.ps1"
pause
