@echo off
rem Double-click to stop DataGatherer. Your data is kept.
cd /d "%~dp0"
docker compose --env-file .env.docker down
echo.
echo DataGatherer is stopped. Your data is kept; double-click start.bat to start it again.
pause
