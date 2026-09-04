import pytest
from backend.skills.ship30 import generate_ship30_essay
from backend.schemas import Citation

@pytest.mark.asyncio
async def test_ship30_essay_skill():
    citations = [
        Citation(
            title="Product-Led Growth",
            guest="Elena Verna",
            source="Lenny's Podcast",
            snippet="PLG is an organizational product distribution model.",
            score=2.5
        )
    ]
    essay, provider = await generate_ship30_essay("PLG Monetization", citations)
    assert "# " in essay
    assert "Elena Verna" in essay or "Pillar" in essay
    assert len(essay.split()) > 150
