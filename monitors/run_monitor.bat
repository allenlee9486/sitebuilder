@echo off
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
cd /d "%~dp0.."
"C:\Users\86159\AppData\Local\Programs\Python\Python313\python.exe" monitors/report_all.py >> monitors/scheduler.log 2>&1
