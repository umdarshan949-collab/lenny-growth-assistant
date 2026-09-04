import os
import re
from typing import List, Dict, Any
from sqlalchemy import select, delete
from backend.database import AsyncSessionLocal
from backend.models import Transcript, TranscriptChunk

TRANSCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "transcripts")

def parse_transcript_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    title = "Lenny's Podcast Transcript"
    guest = "Guest Expert"
    host = "Lenny Rachitsky"
    source = "Lenny's Podcast"
    body_start_idx = 0

    for i, line in enumerate(lines[:10]):
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
            body_start_idx = i + 1
        elif line.startswith("Guest:"):
            guest = line.replace("Guest:", "").strip()
            body_start_idx = i + 1
        elif line.startswith("Host:"):
            host = line.replace("Host:", "").strip()
            body_start_idx = i + 1
        elif line.startswith("Source:"):
            source = line.replace("Source:", "").strip()
            body_start_idx = i + 1

    body_text = "\n".join(lines[body_start_idx:]).strip()
    return {
        "title": title,
        "guest": guest,
        "host": host,
        "source": source,
        "file_path": file_path,
        "text": body_text
    }

def chunk_text(text: str, chunk_size: int = 350, overlap: int = 70) -> List[str]:
    words = text.split()
    if not words:
        return []
    
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= len(words):
            break
        i += (chunk_size - overlap)
    return chunks

def extract_keywords(text: str) -> str:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {"the", "and", "that", "this", "for", "with", "you", "are", "have", "from", "was", "will", "what", "how", "can"}
    keywords = set(w for w in words if w not in stopwords)
    return " ".join(keywords)

async def run_ingestion():
    if not os.path.exists(TRANSCRIPTS_DIR):
        print(f"Transcripts directory not found: {TRANSCRIPTS_DIR}")
        return

    from backend.database import init_db
    await init_db()

    async with AsyncSessionLocal() as session:
        # Clear old transcripts for clean re-ingestion
        await session.execute(delete(TranscriptChunk))
        await session.execute(delete(Transcript))
        await session.commit()

        for filename in os.listdir(TRANSCRIPTS_DIR):
            if filename.endswith(".txt"):
                file_path = os.path.join(TRANSCRIPTS_DIR, filename)
                parsed = parse_transcript_file(file_path)

                transcript_obj = Transcript(
                    title=parsed["title"],
                    guest=parsed["guest"],
                    host=parsed["host"],
                    source=parsed["source"],
                    file_path=file_path
                )
                session.add(transcript_obj)
                await session.flush() # Get generated ID

                chunks = chunk_text(parsed["text"])
                for idx, chunk_str in enumerate(chunks):
                    kw = extract_keywords(chunk_str)
                    chunk_obj = TranscriptChunk(
                        transcript_id=transcript_obj.id,
                        chunk_index=idx,
                        text=chunk_str,
                        keywords=kw
                    )
                    session.add(chunk_obj)
        
        await session.commit()
        print("Transcript ingestion completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ingestion())
