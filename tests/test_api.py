import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/config/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "The Lenny Growth Assistant" in data["project"]

@pytest.mark.asyncio
async def test_config_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/config")
        assert res.status_code == 200
        data = res.json()
        assert "active_provider" in data

        set_res = await ac.post("/api/config/provider?provider=ollama")
        assert set_res.status_code == 200
        assert set_res.json()["active_provider"] == "ollama"

@pytest.mark.asyncio
async def test_sessions_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create session
        create_res = await ac.post("/api/sessions", params={"title": "Test Session"})
        assert create_res.status_code == 200
        sess_data = create_res.json()
        sess_id = sess_data["id"]

        # List sessions
        list_res = await ac.get("/api/sessions")
        assert list_res.status_code == 200
        assert any(s["id"] == sess_id for s in list_res.json())

        # Detail session
        detail_res = await ac.get(f"/api/sessions/{sess_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == sess_id

        # Delete session
        del_res = await ac.delete(f"/api/sessions/{sess_id}")
        assert del_res.status_code == 200

@pytest.mark.asyncio
async def test_chat_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        chat_res = await ac.post(
            "/api/chat",
            json={"message": "What is Shreyas Doshi LNO framework?", "provider": "ollama"}
        )
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert "session_id" in data
        assert "content" in data
        assert "citations" in data
