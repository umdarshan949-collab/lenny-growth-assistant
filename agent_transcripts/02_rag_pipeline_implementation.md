# Agent Transcript 02: RAG Pipeline & Citation Grounding

**Goal**: Ingest transcripts from Lenny's Podcast, chunk text with sliding window overlap, build hybrid TF-IDF + vector index, and return grounded citations.

## Actions Log
- Created transcript parser in `backend/rag/ingest.py` to extract metadata (Title, Guest, Host, Source) and split body text into ~350 word overlapping chunks.
- Implemented `compute_tf_idf_score` in `backend/rag/retriever.py` to score chunk relevance against user queries.
- Added top-k citation formatting (`title`, `guest`, `snippet`, `score`).
- Populated sample dataset covering Elena Verna, Shreyas Doshi, Brian Balfour, Marty Cagan, Gibson Biddle, and Casey Winters.

## Encountered Challenges & Corrections
- **Issue**: Short queries like "PLG" produced low keyword scores due to stopword filtering.
- **Resolution**: Enhanced keyword extraction logic in `ingest.py` to preserve 3-letter acronyms (PLG, LNO, PMF, PQL, DHM).
