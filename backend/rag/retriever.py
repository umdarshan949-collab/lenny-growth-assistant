import re
import math
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.database import AsyncSessionLocal
from backend.models import TranscriptChunk, Transcript
from backend.schemas import Citation

def compute_tf_idf_score(query: str, chunk_text: str, keywords: str) -> float:
    query_terms = [q.lower() for q in re.findall(r'\b[a-zA-Z]{3,}\b', query)]
    if not query_terms:
        return 0.0

    chunk_lower = chunk_text.lower()
    kw_lower = (keywords or "").lower()

    score = 0.0
    for term in query_terms:
        # Frequency in chunk text
        count_text = len(re.findall(r'\b' + re.escape(term) + r'\b', chunk_lower))
        count_kw = len(re.findall(r'\b' + re.escape(term) + r'\b', kw_lower))

        if count_text > 0:
            score += (1.0 + math.log(count_text)) * 1.5
        if count_kw > 0:
            score += 0.8

    return score

async def retrieve_relevant_chunks(query: str, top_k: int = 3) -> List[Citation]:
    async with AsyncSessionLocal() as session:
        stmt = select(TranscriptChunk).options(selectinload(TranscriptChunk.transcript))
        result = await session.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            return []

        scored_chunks = []
        for chunk in chunks:
            score = compute_tf_idf_score(query, chunk.text, chunk.keywords)
            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_chunks[:top_k]

        citations = []
        for score, chunk in top_matches:
            # Create a 250-character snippet for preview
            snippet = chunk.text[:280] + "..." if len(chunk.text) > 280 else chunk.text
            citations.append(
                Citation(
                    title=chunk.transcript.title,
                    guest=chunk.transcript.guest,
                    source=chunk.transcript.source,
                    snippet=snippet,
                    score=round(score, 2)
                )
            )
        
        return citations
