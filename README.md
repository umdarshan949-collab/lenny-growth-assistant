# The Lenny Growth Assistant 🚀

**The Lenny Growth Assistant** is a full-stack, AI-powered conversational web application designed to answer product management and growth strategy questions strictly grounded in transcripts from **Lenny's Podcast**. 

It features source-grounded citations, flexible multi-model configuration (**Ollama**, **Anthropic Claude**, **OpenAI**), a dedicated **Ship 30 for 30** content generation skill, an in-app side-by-side **Artifact Viewer** with sandboxed iframe isolation, persistent chat session storage, automated unit tests, and full Docker Compose support.

---

## 🌟 Key Features

1. **Grounded Conversational RAG**: Answers product management questions using a hybrid search engine over curated transcripts (Shreyas Doshi, Elena Verna, Brian Balfour, Marty Cagan, Gibson Biddle, Casey Winters). Every response includes expandable source citation pills.
2. **Flexible LLM Configuration Layer**:
   - **Local LLM (Mandatory Demo)**: Powered by **Ollama** (`llama3.2`).
   - **Cloud LLMs**: Hot-swappable support for **Anthropic Claude 3.5 Sonnet** and **OpenAI GPT-4o**.
   - **Graceful Fallback**: Automatically falls back to local grounded synthesis if API keys or services are unreachable.
3. **Ship 30 for 30 Content Skill**: Dedicated skill generator producing ~1,250-word atomic essays adhering to Ship 30 writing principles (Hook, Subhead, Problem, Core Framework, Actionable Bullets, Bold Emphasis, Specific Takeaway).
4. **Claude-Style In-App Artifact Viewer**: Renders generated HTML/CSS components and Markdown documents side-by-side with the chat. Enforces `sandbox="allow-scripts"` iframe security.
5. **Persistence**: Async SQLAlchemy database storing session history, messages, citations, and artifacts in zero-config SQLite or PostgreSQL.
6. **Automated Test Suite**: Full pytest coverage for API contracts, RAG retrieval, LLM fallback, and Ship 30 skill formatting.

---

## 🏗️ Architecture Overview

```
lenny-growth-assistant/
├── README.md               # Main Documentation & Setup Guide
├── PRD.md                  # Product Requirements & Forward Deployed Brief
├── design.md               # UI/UX Specifications & Interaction States
├── architecture.md         # Database Schema, API Contracts & Topology
├── docker-compose.yml      # Docker Compose setup (FastAPI + PostgreSQL + Ollama)
├── Dockerfile              # Container definition for FastAPI backend
├── .env.example            # Environment variables template
├── requirements.txt        # Python backend dependencies
├── run.bat / run.sh        # One-command quickstart scripts
├── data/
│   └── transcripts/        # Raw podcast transcripts dataset
├── backend/
│   ├── main.py             # FastAPI entry point & static file server
│   ├── config.py           # Environment settings
│   ├── database.py         # Async SQLAlchemy engine (SQLite/PostgreSQL)
│   ├── models.py           # Relational ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── rag/                # Transcript ingestion & hybrid retriever
│   ├── llm/                # Flexible provider layer (Ollama, Anthropic, OpenAI)
│   ├── skills/             # Ship 30 for 30 content skill engine
│   └── routes/             # API endpoints (chat, sessions, skills, artifacts, config)
├── frontend/               # Modern SPA (HTML5, CSS3, Vanilla JS)
├── tests/                  # Automated pytest test suite
└── agent_transcripts/      # AI coding agent trajectory logs
```

---

## ⚡ Quick Start Guide (One-Command Run)

### Prerequisites
- **Python 3.10+** installed.
- (Optional) **Ollama** installed and running (`ollama run llama3.2`).
- (Optional) **Docker Desktop** installed.

---

### Option 1: Native Local Run (Recommended for Evaluation)

#### Windows:
```cmd
run.bat
```

#### Linux / macOS:
```bash
chmod +x run.sh
./run.sh
```

The script will automatically:
1. Create a Python virtual environment (`venv`).
2. Install dependencies from `requirements.txt`.
3. Ingest and index transcript files.
4. Run the automated `pytest` test suite.
5. Launch the application at **`http://localhost:8000`**.

---

### Option 2: Manual Step-by-Step Setup

1. **Clone & Navigate**:
   ```bash
   cd lenny-growth-assistant
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   ```bash
   cp .env.example .env
   ```

5. **Ingest Knowledge Base**:
   ```bash
   python -m backend.rag.ingest
   ```

6. **Run Automated Tests**:
   ```bash
   pytest -v
   ```

7. **Start FastAPI Backend**:
   ```bash
   python -m backend.main
   ```
   Open **`http://localhost:8000`** in your web browser.

---

### Option 3: Docker Compose Run

To run the entire stack (FastAPI + PostgreSQL + Ollama) in containers:

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Automated & Manual Testing

### Automated Test Suite
Run the full test suite with verbose output:
```bash
pytest -v
```

Tests cover:
- `tests/test_api.py`: FastAPI endpoints, session CRUD, and health check.
- `tests/test_rag.py`: Transcript chunking, TF-IDF scoring, and citation extraction.
- `tests/test_llm.py`: Multi-provider switching and fallback behavior.
- `tests/test_skills.py`: Ship 30 for 30 essay structure and word count.

### Manual UI Test Plan
1. **Chat Grounding**: Type `"What is Shreyas Doshi's LNO framework?"`. Verify that citation pills appear below the response with quote snippets and transcript title.
2. **Model Toggle**: Change provider in the top header from `Ollama` to `Anthropic` or `OpenAI`. Send a message and observe the provider badge update.
3. **Ship 30 Skill**: Click **Generate Ship 30 Essay**, enter topic `"PLG Monetization"`, and verify a ~1,250-word atomic essay opens in the right-side Artifact Viewer.
4. **HTML Artifact Security**: Click **Generate HTML Dashboard Artifact**. Verify that the rendered component appears inside a sandboxed iframe with `sandbox="allow-scripts"`. Switch to the **Code** tab to verify raw source viewing.

---

## 📽️ Demo Video Script Guide (for Candidate Recording)

When recording your 2–3 minute video presentation:
1. **Introduction (30s)**: Introduce yourself, state the problem (turning raw transcripts into actionable, grounded advice), and present your solution architecture.
2. **Product Walkthrough (60s)**: Show the chat interface, demonstrate a grounded query, point out the citation pills, and trigger the **Ship 30 for 30** essay skill.
3. **Local Ollama & Model Toggle (30s)**: Show local Ollama running in the background, switch model providers in the UI header, and highlight the automatic fallback resilience.
4. **Technical Trade-Offs (30s)**: Explain your decision to use zero-config hybrid retrieval for zero-cost deployment and iframe sandbox isolation for secure artifact rendering.

---

## 🔧 Troubleshooting

- **Ollama Connection Refused**: Ensure Ollama service is running (`ollama serve` or `ollama run llama3.2`). If offline, the app automatically uses local grounded synthesis.
- **Port 8000 Already in Use**: Change `PORT=8080` in `.env` or run `uvicorn backend.main:app --port 8080`.
- **Database Lock Errors**: The app uses `sqlite+aiosqlite` for zero-setup local storage. Delete `lenny.db` to re-trigger a clean database setup if needed.
