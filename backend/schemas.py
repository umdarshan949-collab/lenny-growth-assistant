from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Citation(BaseModel):
    title: str
    guest: Optional[str] = None
    source: Optional[str] = None
    snippet: str
    score: float

class ChatMessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    provider: Optional[str] = None # 'ollama', 'anthropic', 'openai'

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    content: str
    citations: List[Citation] = []
    provider_used: str
    artifact: Optional[Dict[str, Any]] = None

class SessionSchema(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SessionDetailSchema(SessionSchema):
    messages: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []

class ArtifactSchema(BaseModel):
    id: str
    session_id: str
    title: str
    type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class Ship30Request(BaseModel):
    session_id: Optional[str] = None
    topic: str
    provider: Optional[str] = None

class ModelConfigSchema(BaseModel):
    active_provider: str
    ollama_url: str
    ollama_model: str
    anthropic_available: bool
    openai_available: bool
