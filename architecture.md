# Architecture & Technical Specifications: The Lenny Growth Assistant

## 1. System Architecture Overview

The Lenny Growth Assistant follows a clean, decoupled full-stack architecture:

```
[ Frontend SPA (HTML5/CSS3/Vanilla JS) ]
                   │
                   ▼ REST API (FastAPI)
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Chat Router  │  │ Sessions     │  │ Skills       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
│         ▼                 ▼                 ▼          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            RAG Knowledge Base & Retriever        │  │
│  │   (BM25 + TF-IDF Hybrid Search over Transcripts) │  │
│  └────────────────────────┬─────────────────────────┘  │
│                           │                            │
│                           ▼                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │             LLM Provider Abstraction            │  │
│  │  (Ollama Local <-> Anthropic Claude <-> OpenAI)  │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────┘
                            │ Async ORM
                            ▼
           ┌──────────────────────────────────┐
           │ Database (SQLite / PostgreSQL)   │
           │ Sessions, Messages, Artifacts    │
           └──────────────────────────────────┘
```

---

## 2. Database Schema (Entity Relationship Diagram)

```
┌───────────────────┐        ┌───────────────────┐
│     sessions      │        │     messages      │
├───────────────────┤        ├───────────────────┤
│ id (PK, String)   │◄───────┤ id (PK, String)   │
│ title (String)    │ 1    N │ session_id (FK)   │
│ created_at        │        │ role (String)     │
│ updated_at        │        │ content (Text)    │
└─────────┬─────────┘        │ citations (JSON)  │
          │                  │ provider (String) │
          │ 1                └───────────────────┘
          │
          │ N                ┌───────────────────┐
          └─────────────────►│     artifacts     │
                             ├───────────────────┤
                             │ id (PK, String)   │
                             │ session_id (FK)   │
                             │ title (String)    │
                             │ type (String)     │
                             │ content (Text)    │
                             └───────────────────┘
```

---

## 3. API Endpoint Specifications

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/chat` | Send chat message & get grounded answer | `{ session_id, message, provider }` | `ChatResponse` (message, citations, artifact) |
| `GET` | `/api/sessions` | List all chat sessions | None | `List[SessionSchema]` |
| `GET` | `/api/sessions/{id}` | Get session message history & artifacts | None | `SessionDetailSchema` |
| `DELETE` | `/api/sessions/{id}` | Delete session | None | `{ status: "success" }` |
| `POST` | `/api/skills/ship30` | Execute Ship 30 for 30 essay skill | `{ session_id, topic, provider }` | `ChatResponse` with essay & artifact |
| `GET` | `/api/artifacts/{id}` | Get specific artifact details | None | `ArtifactSchema` |
| `GET` | `/api/config` | Get LLM providers status | None | `ModelConfigSchema` |
| `POST` | `/api/config/provider` | Switch active LLM provider | Query: `provider` | `{ active_provider }` |
| `GET` | `/api/config/health` | Health check endpoint | None | `{ status: "healthy" }` |

---

## 4. RAG Ingestion & Hybrid Retrieval Pipeline

1. **Document Loading**: Parse `.txt` transcript files in `data/transcripts/`, extracting metadata headers (`Title`, `Guest`, `Host`, `Source`).
2. **Chunking**: Split transcript text into overlapping chunks (~350 words, 70 word overlap) to preserve semantic context across chunk boundaries.
3. **Keyword & Vector Indexing**: Extract domain keywords (e.g. `PLG`, `LNO`, `PQL`, `DHM`, `PMF`, `retention`) and calculate TF-IDF relevance scores.
4. **Hybrid Retrieval**: When a query arrives, retrieve top matching chunks, score them against user intent, and format them into structured `Citation` objects.

---

## 5. Flexible LLM Layer & Fallback Logic

```
                    [ Incoming User Request ]
                                │
                                ▼
                   Active Provider Selected?
                   /            |            \
                  /             |             \
                 v              v              v
           [ Ollama ]     [ Anthropic ]    [ OpenAI ]
            (Local)         (Claude)        (GPT-4o)
                │               │              │
        Service Offline?    Key Missing?   Key Missing?
                │               │              │
                └───────────────┼──────────────┘
                                │
                                ▼ Fallback
                  [ Local Grounded Synthesis Engine ]
                (Formats exact transcript citations)
```

---

## 6. Security Isolation Architecture for Artifact Rendering

To prevent untrusted generated HTML/CSS code from executing malicious scripts in the user's browser context:
- HTML artifacts are rendered exclusively inside an `<iframe>` container.
- The iframe includes `sandbox="allow-scripts"`, which strictly isolates the rendered artifact from:
  - Parent window DOM access (`window.parent`)
  - Session cookies and LocalStorage access
  - Top-level navigation hijacking
