import pytest
from backend.llm.provider import get_llm_provider, OllamaProvider, AnthropicProvider, OpenAIProvider, LocalFallbackProvider

@pytest.mark.asyncio
async def test_llm_provider_factory():
    p_ollama = get_llm_provider("ollama")
    assert isinstance(p_ollama, OllamaProvider)

    p_anthropic = get_llm_provider("anthropic")
    assert isinstance(p_anthropic, AnthropicProvider)

    p_openai = get_llm_provider("openai")
    assert isinstance(p_openai, OpenAIProvider)

@pytest.mark.asyncio
async def test_fallback_provider():
    fallback = LocalFallbackProvider()
    response, name = await fallback.generate("What is Product Led Growth?")
    assert "Grounded Response" in response
    assert name == "Local Engine (Fallback)"
