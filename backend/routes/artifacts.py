from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from backend.database import get_db
from backend.models import Artifact
from backend.schemas import ArtifactSchema

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])

@router.get("/{artifact_id}", response_model=ArtifactSchema)
async def get_artifact(artifact_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Artifact).where(Artifact.id == artifact_id)
    res = await db.execute(stmt)
    art = res.scalar_one_or_none()
    if not art:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art

@router.get("/session/{session_id}", response_model=List[ArtifactSchema])
async def get_session_artifacts(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Artifact).where(Artifact.session_id == session_id).order_by(Artifact.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()
