from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
from backend.database import get_db
from backend.models import Session, Message, Artifact
from backend.schemas import SessionSchema, SessionDetailSchema

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

@router.get("", response_model=List[SessionSchema])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(Session).order_by(Session.updated_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=SessionSchema)
async def create_session(title: str = "New Chat Session", db: AsyncSession = Depends(get_db)):
    sess = Session(title=title)
    db.add(sess)
    await db.commit()
    await db.refresh(sess)
    return sess

@router.get("/{session_id}", response_model=SessionDetailSchema)
async def get_session_detail(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).options(
        selectinload(Session.messages),
        selectinload(Session.artifacts)
    ).where(Session.id == session_id)
    
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_data = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "provider": m.provider,
            "created_at": m.created_at.isoformat()
        } for m in sess.messages
    ]

    artifacts_data = [
        {
            "id": a.id,
            "title": a.title,
            "type": a.type,
            "content": a.content,
            "created_at": a.created_at.isoformat()
        } for a in sess.artifacts
    ]

    return {
        "id": sess.id,
        "title": sess.title,
        "created_at": sess.created_at,
        "updated_at": sess.updated_at,
        "messages": messages_data,
        "artifacts": artifacts_data
    }

@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = delete(Session).where(Session.id == session_id)
    await db.execute(stmt)
    await db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted."}
