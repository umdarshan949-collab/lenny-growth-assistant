import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.database import init_db, AsyncSessionLocal
from backend.models import Transcript
from backend.rag.ingest import run_ingestion
from backend.routes import chat, sessions, skills, artifacts, config
from sqlalchemy import select

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI assistant grounded in Lenny's Podcast transcripts."
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(skills.router)
app.include_router(artifacts.router)
app.include_router(config.router)

@app.on_event("startup")
async def startup_event():
    print("[Startup] Initializing Database Schema...")
    await init_db()

    # Check if transcripts are already ingested
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Transcript))
        transcripts = res.scalars().all()
        if not transcripts:
            print("[Startup] Auto-ingesting Lenny's Podcast Transcripts...")
            await run_ingestion()
        else:
            print(f"[Startup] Found {len(transcripts)} existing ingested transcripts.")

# Mount Static Frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
