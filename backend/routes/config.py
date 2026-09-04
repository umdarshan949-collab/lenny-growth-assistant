from fastapi import APIRouter, HTTPException
from backend.config import settings
from backend.schemas import ModelConfigSchema

router = APIRouter(prefix="/api/config", tags=["Configuration"])

active_provider = settings.DEFAULT_PROVIDER

@router.get("", response_model=ModelConfigSchema)
async def get_config():
    return ModelConfigSchema(
        active_provider=active_provider,
        ollama_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL,
        anthropic_available=bool(settings.ANTHROPIC_API_KEY),
        openai_available=bool(settings.OPENAI_API_KEY)
    )

@router.post("/provider")
async def set_provider(provider: str):
    global active_provider
    provider_clean = provider.lower().strip()
    if provider_clean not in ["ollama", "anthropic", "openai"]:
        raise HTTPException(status_code=400, detail="Invalid provider. Must be 'ollama', 'anthropic', or 'openai'.")
    
    active_provider = provider_clean
    return {"status": "success", "active_provider": active_provider}

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_provider": active_provider
    }
