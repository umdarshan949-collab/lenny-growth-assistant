from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models import Session, Message, Artifact
from backend.schemas import Ship30Request, ChatResponse
from backend.rag.retriever import retrieve_relevant_chunks
from backend.skills.ship30 import generate_ship30_essay

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.post("/ship30", response_model=ChatResponse)
async def execute_ship30_skill(req: Ship30Request, db: AsyncSession = Depends(get_db)):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    # 1. Session check or create
    session_id = req.session_id
    if not session_id:
        sess = Session(title=f"Ship 30 Essay: {req.topic[:30]}")
        db.add(sess)
        await db.flush()
        session_id = sess.id

    # 2. Retrieve transcript citations for topic
    citations = await retrieve_relevant_chunks(req.topic, top_k=4)

    # 3. Generate Ship 30 Essay via skill
    essay_content, provider_used = await generate_ship30_essay(req.topic, citations, req.provider)

    # 4. Save User prompt message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=f"Generate a Ship 30 for 30 atomic essay on topic: '{req.topic}'"
    )
    db.add(user_msg)
    await db.flush()

    # 5. Create Artifact for the essay so it appears in the side viewer
    artifact_obj = Artifact(
        session_id=session_id,
        title=f"Ship 30 Essay - {req.topic}",
        type="markdown",
        content=essay_content
    )
    db.add(artifact_obj)
    await db.flush()

    # 6. Save Assistant response message
    citation_dicts = [c.model_dump() for c in citations]
    asst_msg = Message(
        session_id=session_id,
        role="assistant",
        content=essay_content,
        citations=citation_dicts,
        provider=provider_used
    )
    db.add(asst_msg)
    await db.commit()

    return ChatResponse(
        session_id=session_id,
        message_id=asst_msg.id,
        role="assistant",
        content=essay_content,
        citations=citations,
        provider_used=provider_used,
        artifact={
            "id": artifact_obj.id,
            "title": artifact_obj.title,
            "type": artifact_obj.type,
            "content": artifact_obj.content
        }
    )
