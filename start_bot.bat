@echo off
title Cortana // J.A.R.V.I.S. Autonomous Daemon
cd /d "%~dp0"
echo ==============================================================
echo 🛰️ LAUNCHING CORTANA // J.A.R.V.I.S. 24/7 AUTONOMOUS COMMAND
echo ==============================================================
.venv\Scripts\python.exe bot.py
pause
