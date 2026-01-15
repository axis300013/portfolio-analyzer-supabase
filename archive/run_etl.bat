@echo off
cd /d "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
call venv\Scripts\activate
python -m backend.app.etl.run_daily_etl
pause
