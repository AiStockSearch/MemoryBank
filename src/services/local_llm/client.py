import aiohttp
from typing import Optional

class LocalLLMClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    async def complete(self, prompt: str, model: str = None, max_tokens: int = 1024) -> Optional[str]:
        url = f"{self.base_url}/v1/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        if model:
            payload["model"] = model
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                # Поддержка разных форматов ответа (Ollama, LM Studio, HF Inference)
                if resp.status == 200:
                    if "choices" in data and data["choices"]:
                        return data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content")
                    if "generated_text" in data:
                        return data["generated_text"]
                return None 