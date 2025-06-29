import aiohttp
from typing import Optional, Dict, List

class SlackClient:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"

    async def send_message(self, channel: str, text: str) -> Optional[Dict]:
        url = f"{self.base_url}/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        payload = {"channel": channel, "text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return data
                return None

    async def list_channels(self) -> List[Dict]:
        url = f"{self.base_url}/conversations.list"
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return data.get("channels", [])
                return [] 