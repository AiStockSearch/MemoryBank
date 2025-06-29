import aiohttp
from typing import Optional, Dict, List

class GDriveClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/drive/v3"
        self.upload_url = "https://www.googleapis.com/upload/drive/v3/files"

    async def list_files(self, query: str = None, page_size: int = 10) -> List[Dict]:
        url = f"{self.base_url}/files"
        params = {"key": self.api_key, "pageSize": str(page_size)}
        if query:
            params["q"] = query
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                return data.get("files", [])

    async def download_file(self, file_id: str) -> Optional[bytes]:
        url = f"{self.base_url}/files/{file_id}"
        params = {"key": self.api_key, "alt": "media"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.read()
                return None

    async def upload_file(self, name: str, data: bytes, mime_type: str = "application/octet-stream") -> Optional[Dict]:
        url = f"{self.upload_url}?uploadType=media&key={self.api_key}"
        headers = {"Content-Type": mime_type}
        params = {"name": name}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                return None 