@echo off
echo ========================================================
echo   Starting The Lenny Growth Assistant
echo ========================================================

IF NOT EXIST venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Ingesting Lenny's Podcast Transcripts...
python -m backend.rag.ingest

echo Running automated tests...
pytest -v

echo Launching FastAPI Server at http://localhost:8000 ...
python -m backend.main
