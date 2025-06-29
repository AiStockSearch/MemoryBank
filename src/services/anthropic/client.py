import aiohttp
from typing import Optional, Dict

class AnthropicClient:
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def complete(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200 and "content" in data:
                    # Claude v3: content — список сообщений
                    if isinstance(data["content"], list):
                        return " ".join([c.get("text", "") for c in data["content"]])
                    return data["content"]
                return None 