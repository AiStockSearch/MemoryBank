import aiohttp
from typing import Optional, Dict, List

class ConfluenceClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    async def get_page(self, page_id: str) -> Optional[Dict]:
        url = f"{self.base_url}/rest/api/content/{page_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def create_page(self, space_key: str, title: str, body: str) -> Optional[Dict]:
        url = f"{self.base_url}/rest/api/content"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage"
                }
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                return None

    async def search_pages(self, cql: str, limit: int = 10) -> List[Dict]:
        url = f"{self.base_url}/rest/api/content/search"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"cql": cql, "limit": str(limit)}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("results", [])
                return [] 