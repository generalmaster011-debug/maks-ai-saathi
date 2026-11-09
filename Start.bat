@echo off
cd /d "%~dp0"
echo [1/3] Python venv...
if not exist .venv (py -3.13 -m venv .venv || python -m venv .venv)
echo [2/3] Installing (2-5 min)...
.venv\Scripts\python -m pip install -q --upgrade pip
.venv\Scripts\python -m pip install -q -r requirements.txt
echo [3/3] Gemini key...
.venv\Scripts\python copy_key.py
echo.
echo Starting app... browser ma http://127.0.0.1:7860 kholo
.venv\Scripts\python app.py
pause
