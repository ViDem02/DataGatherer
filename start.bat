@echo off
rem Double-click to start DataGatherer (needs Docker Desktop).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
echo.
pause
