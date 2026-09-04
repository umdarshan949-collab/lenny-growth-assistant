# Product Requirements Document (PRD): The Lenny Growth Assistant

## 1. Executive Summary & Forward Deployed Brief

### 1.1 User & Problem Statement
Product managers, founders, and growth leads face a constant challenge when seeking tactical advice: general-purpose LLMs produce generic, ungrounded responses that lack context and practical rigor. Meanwhile, **Lenny's Podcast and Newsletter** contains thousands of hours of high-leverage frameworks from top product leaders (Elena Verna, Shreyas Doshi, Brian Balfour, Marty Cagan, Gibson Biddle, Casey Winters). 

**The Lenny Growth Assistant** bridges this gap by providing an AI-powered conversational interface strictly grounded in Lenny's Podcast transcripts. It allows users to ask complex product management questions, receive grounded answers with transcript source citations, generate structured Ship 30 for 30 atomic essays, and render interactive HTML/CSS artifacts directly inside the product.

### 1.2 Target Personas
- **Senior PMs & Group PMs**: Seeking tactical frameworks (e.g. LNO framework, Pre-Mortems) to optimize time leverage and team execution.
- **Growth Leaders & Growth PMs**: Designing self-serve PLG motions, product qualified lead (PQL) rules, and closed-loop retention engines.
- **Founders & CPOs**: Evaluating Market-Product-Channel-Model fit and hard-to-copy competitive advantages (DHM Model).

---

## 2. Success Metrics

| Metric Category | Target Metric | Measurement Method |
| :--- | :--- | :--- |
| **Grounding Accuracy** | >= 95% of factual claims backed by explicit transcript citations | Citation verification in test suite |
| **Response Latency** | < 2.5s initial response time on local Ollama / Cloud LLMs | API response logging |
| **Artifact Security** | 100% iframe sandbox isolation for rendered HTML artifacts | Security assertion test suite |
| **User Engagement** | Average 4+ queries per session, 1+ Ship 30 essay generated per user | Session telemetry analytics |

---

## 3. Core Requirements & Scope Choices

### 3.1 Included Scope
1. **Grounded Conversational Interface**: RAG engine retrieving relevant transcript chunks with title, speaker, and quote snippet citations.
2. **Flexible LLM Provider Configuration**: Hot-swappable model engine supporting local **Ollama** (`llama3.2`), **Anthropic Claude 3.5**, and **OpenAI GPT-4o**, with automatic local fallback if API keys or services are unavailable.
3. **Ship 30 for 30 Content Skill**: Dedicated skill producing ~1,250-word atomic essays adhering to Ship 30 writing principles (Hook, Subhead, Problem, Core Framework, Actionable Bullets, Bold Emphasis, Specific Takeaway).
4. **Claude-Style In-App Artifact Viewer**: Side-by-side split screen rendering generated HTML/CSS components inside a sandboxed iframe (`sandbox="allow-scripts"`) and raw Markdown.
5. **Persistence**: Async SQLAlchemy database storing session history, messages, citations, and generated artifacts in SQLite (zero-config) and PostgreSQL.

### 3.2 Intentionally Excluded Scope
- **Paid Third-Party Vector DB Dependencies**: Excluded external paid vector DBs (e.g. Pinecone) to ensure zero-cost out-of-the-box local execution. Built an in-memory/DB hybrid TF-IDF + vector cosine retriever instead.
- **User Authentication / OAuth**: Kept user sessions cookie/session-ID based for fast, frictionless evaluator testing.

---

## 4. Key Technical Assumptions & Risks

### 4.1 Technical Assumptions
1. Evaluator machine has Python 3.10+ installed and optionally Ollama running on `http://localhost:11434`.
2. SQLite handles local development; PostgreSQL handles Docker production deployment.

### 4.2 Risk Matrix & Mitigation Strategies

> [!WARNING]
> **Risk 1: Hallucinations / Unbacked Claims**
> *Mitigation*: Strictly enforce system prompt constraints requiring transcript context injection and mandatory source citation pills.

> [!IMPORTANT]
> **Risk 2: HTML Artifact Security (XSS / DOM Theft)**
> *Mitigation*: Render all generated HTML inside an isolated `<iframe>` element enforced with `sandbox="allow-scripts"`, preventing access to parent window, cookies, or local storage.

> [!NOTE]
> **Risk 3: Model Unavailability / Missing Cloud Keys**
> *Mitigation*: Implement graceful multi-tier fallback: `Cloud API` -> `Local Ollama` -> `Local Grounded Synthesis Engine`.
