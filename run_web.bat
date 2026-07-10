@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt -q
python -m monitor.web_app %*
