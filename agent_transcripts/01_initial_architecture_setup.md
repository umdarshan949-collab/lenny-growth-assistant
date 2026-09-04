# Agent Transcript 01: Initial Architecture & Database Setup

**Goal**: Establish the project directory, FastAPI backend, SQLAlchemy database ORM models, Pydantic schemas, and environment configuration.

## Actions Log
- Defined Pydantic settings in `backend/config.py` for dynamic provider switching (`DEFAULT_PROVIDER=ollama`).
- Created async SQLAlchemy database engine (`backend/database.py`) supporting zero-config SQLite (`sqlite+aiosqlite:///./lenny.db`) and PostgreSQL (`postgresql+asyncpg://...`).
- Designed relational schema in `backend/models.py` (`Session`, `Message`, `Artifact`, `Transcript`, `TranscriptChunk`).
- Configured FastAPI routers (`chat`, `sessions`, `skills`, `artifacts`, `config`).

## Encountered Challenges & Corrections
- **Issue**: SQLite async driver required `check_same_thread=False` to prevent thread locking errors during startup table initialization.
- **Resolution**: Updated `backend/database.py` with conditional `connect_args` for SQLite.
