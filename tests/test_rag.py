import pytest
from backend.rag.ingest import chunk_text, extract_keywords
from backend.rag.retriever import retrieve_relevant_chunks, compute_tf_idf_score

def test_chunk_text():
    sample = " ".join([f"word{i}" for i in range(500)])
    chunks = chunk_text(sample, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert len(chunks[0].split()) == 100

def test_extract_keywords():
    text = "Product-Led Growth PLG monetization strategy and retention loops"
    kw = extract_keywords(text)
    assert "product" in kw
    assert "growth" in kw
    assert "retention" in kw

def test_tf_idf_scoring():
    query = "LNO framework Shreyas Doshi"
    chunk = "Shreyas Doshi explains the LNO framework for PM time leverage."
    score = compute_tf_idf_score(query, chunk, "lno framework pm time")
    assert score > 0.0

@pytest.mark.asyncio
async def test_retriever():
    citations = await retrieve_relevant_chunks("Elena Verna PLG PQL", top_k=2)
    assert isinstance(citations, list)
    if citations:
        assert citations[0].snippet is not None
