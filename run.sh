#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  Starting The Lenny Growth Assistant"
echo "========================================================"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Ingesting Lenny's Podcast Transcripts..."
python3 -m backend.rag.ingest

echo "Running automated tests..."
pytest -v

echo "Launching FastAPI Server at http://localhost:8000 ..."
python3 -m backend.main
