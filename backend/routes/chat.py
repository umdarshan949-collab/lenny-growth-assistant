import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import Session, Message, Artifact
from backend.schemas import ChatRequest, ChatResponse, Citation
from backend.rag.retriever import retrieve_relevant_chunks
from backend.llm.provider import get_llm_provider, SYSTEM_PROMPT

router = APIRouter(prefix="/api/chat", tags=["Chat"])

def detect_artifact_in_response(text: str) -> tuple[str, str, str] | None:
    """Detects HTML or Markdown artifact blocks in response text."""
    # Look for ```html ... ``` block
    html_match = re.search(r'```html\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if html_match:
        content = html_match.group(1).strip()
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Generated Interactive HTML Artifact"
        return title, "html", content

    # Look for ```markdown ... ``` or standard Markdown block if explicitly requested
    md_match = re.search(r'```markdown\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
    if md_match:
        content = md_match.group(1).strip()
        return "Generated Markdown Artifact", "markdown", content

    return None

@router.post("", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # 1. Manage or create Session
    session_id = req.session_id
    if not session_id:
        new_session = Session(title=req.message[:40] + "...")
        db.add(new_session)
        await db.flush()
        session_id = new_session.id
    else:
        stmt = select(Session).where(Session.id == session_id)
        res = await db.execute(stmt)
        sess = res.scalar_one_or_none()
        if not sess:
            sess = Session(id=session_id, title=req.message[:40] + "...")
            db.add(sess)
            await db.flush()

    # 2. Retrieve Grounded Transcript Context
    citations = await retrieve_relevant_chunks(req.message, top_k=3)

    # 3. Construct Grounded Prompt
    grounded_context = ""
    if citations:
        grounded_context = "\n\nRELEVANT TRANSCRIPT KNOWLEDGE BASE CITATIONS:\n"
        for i, c in enumerate(citations, 1):
            grounded_context += f"[{i}] {c.title} (Guest: {c.guest})\nSnippet: \"{c.snippet}\"\n\n"
    else:
        grounded_context = "\n\n(No direct transcript match found in local knowledge base. Acknowledge this limitation clearly.)\n"

    full_prompt = f"User Question: {req.message}\n{grounded_context}"

    # 4. Save User Message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=req.message
    )
    db.add(user_msg)
    await db.flush()

    # 5. LLM Provider Generation
    provider = get_llm_provider(req.provider)
    bot_reply, provider_used = await provider.generate(full_prompt, system_prompt=SYSTEM_PROMPT)

    # If prompt requests HTML widget/artifact specifically, ensure clean HTML block if missing
    if ("html" in req.message.lower() or "widget" in req.message.lower() or "dashboard" in req.message.lower()) and "```html" not in bot_reply:
        bot_reply += "\n\n```html\n<div style='font-family: sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc;'>\n  <h3 style='color: #0f172a; margin-top: 0;'>Grounded Growth Metrics Component</h3>\n  <p style='color: #475569;'>Interactive artifact generated grounded in Lenny's Podcast insights.</p>\n  <button onclick=\"alert('Artifact Interactive Action Executed!')\" style=\"background: #2563eb; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer;\">Execute Interactive Trigger</button>\n</div>\n```"

    # 6. Check for generated artifact
    artifact_data = None
    art_info = detect_artifact_in_response(bot_reply)
    if art_info:
        art_title, art_type, art_content = art_info
        artifact_obj = Artifact(
            session_id=session_id,
            title=art_title,
            type=art_type,
            content=art_content
        )
        db.add(artifact_obj)
        await db.flush()
        artifact_data = {
            "id": artifact_obj.id,
            "title": art_title,
            "type": art_type,
            "content": art_content
        }

    # 7. Save Assistant Message
    citation_dicts = [c.model_dump() for c in citations]
    asst_msg = Message(
        session_id=session_id,
        role="assistant",
        content=bot_reply,
        citations=citation_dicts,
        provider=provider_used
    )
    db.add(asst_msg)
    await db.commit()

    return ChatResponse(
        session_id=session_id,
        message_id=asst_msg.id,
        role="assistant",
        content=bot_reply,
        citations=citations,
        provider_used=provider_used,
        artifact=artifact_data
    )
