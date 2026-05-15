@echo off
set PYTHONIOENCODING=utf-8
cd /d "D:\开发设计工具\sitebuilder"
"C:\Users\donut\AppData\Local\Programs\Python\Python313\python.exe" monitors/report_all.py >> monitors/scheduler.log 2>&1
