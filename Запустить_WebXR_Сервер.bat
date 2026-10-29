@echo off
chcp 65001 > nul
title WebXR_Station_Server_8000
cls

cd /d "%~dp0"
python scripts\run_server.py

pause
