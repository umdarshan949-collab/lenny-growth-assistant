import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    VERSION: str = "1.0.0"
    
    # Active LLM Provider: 'ollama', 'anthropic', 'openai'
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")
    
    # Ollama Local Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Cloud API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database URL (SQLite async by default for zero-setup, supports PostgreSQL asyncpg)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./lenny.db")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
