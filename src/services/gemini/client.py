import aiohttp
from typing import Optional

class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def complete(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {"maxOutputTokens": max_tokens}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, params=params, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200 and "candidates" in data:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                return None 