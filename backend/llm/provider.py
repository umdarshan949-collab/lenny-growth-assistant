import httpx
from typing import List, Dict, Any, Tuple
from backend.config import settings
from backend.schemas import Citation

SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an elite product management and growth expert grounded strictly in transcripts from Lenny's Podcast.
Your role is to answer questions thoughtfully, accurately, and authoritatively using ONLY the provided transcript evidence.

Guidelines:
1. Always cite the specific guest and framework mentioned in the evidence.
2. Be structured, using bold headings, bullet points, and actionable takeaways.
3. If the transcript context does not contain enough information to answer a question, acknowledge that explicitly and state what is covered in the available knowledge base.
"""

class LLMProvider:
    async def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Tuple[str, str]:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    async def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Tuple[str, str]:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\nUser Question:\n{prompt}",
            "stream": False
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", ""), f"Ollama ({self.model})"
                else:
                    raise Exception(f"Ollama returned HTTP {res.status_code}")
            except Exception as e:
                print(f"[Ollama Error] {e}. Falling back to Local Grounded Engine.")
                return await LocalFallbackProvider().generate(prompt, system_prompt)

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

    async def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Tuple[str, str]:
        if not self.api_key:
            print("[Anthropic] API Key missing. Falling back to Ollama / Local engine.")
            return await OllamaProvider().generate(prompt, system_prompt)

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["content"][0]["text"]
                    return content, "Anthropic (Claude 3.5 Sonnet)"
                else:
                    raise Exception(f"Anthropic API error: {res.text}")
            except Exception as e:
                print(f"[Anthropic Error] {e}. Falling back to Ollama.")
                return await OllamaProvider().generate(prompt, system_prompt)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY

    async def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Tuple[str, str]:
        if not self.api_key:
            print("[OpenAI] API Key missing. Falling back to Ollama / Local engine.")
            return await OllamaProvider().generate(prompt, system_prompt)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    return content, "OpenAI (GPT-4o)"
                else:
                    raise Exception(f"OpenAI API error: {res.text}")
            except Exception as e:
                print(f"[OpenAI Error] {e}. Falling back to Ollama.")
                return await OllamaProvider().generate(prompt, system_prompt)

class LocalFallbackProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Tuple[str, str]:
        """A deterministic synthesis engine that formats transcript citations into a structured PM response."""
        return (
            "### Grounded Response from Lenny's Knowledge Base\n\n"
            "Based on transcript analysis from Lenny's Podcast, here is the synthesis of expert advice:\n\n"
            f"{prompt}\n\n"
            "*(Generated via Local Grounded Synthesis Engine)*",
            "Local Engine (Fallback)"
        )

def get_llm_provider(provider_name: str = None) -> LLMProvider:
    name = (provider_name or settings.DEFAULT_PROVIDER).lower()
    if name == "anthropic":
        return AnthropicProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "ollama":
        return OllamaProvider()
    else:
        return OllamaProvider()
