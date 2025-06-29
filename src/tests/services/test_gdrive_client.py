import pytest
from src.services.gdrive.client import GDriveClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_list_files_success():
    client = GDriveClient("test-key")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.json = AsyncMock(return_value={"files": [{"id": "1"}, {"id": "2"}]})
        mock_get.return_value.__aenter__.return_value = mock_resp
        files = await client.list_files()
        assert len(files) == 2
        assert files[0]["id"] == "1"

@pytest.mark.asyncio
async def test_download_file_success():
    client = GDriveClient("test-key")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=b"data")
        mock_get.return_value.__aenter__.return_value = mock_resp
        data = await client.download_file("1A2B3C4D")
        assert data == b"data"

@pytest.mark.asyncio
async def test_download_file_not_found():
    client = GDriveClient("test-key")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_get.return_value.__aenter__.return_value = mock_resp
        data = await client.download_file("notfound")
        assert data is None

@pytest.mark.asyncio
async def test_upload_file_success():
    client = GDriveClient("test-key")
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"id": "1", "name": "test.txt"})
        mock_post.return_value.__aenter__.return_value = mock_resp
        resp = await client.upload_file("test.txt", b"data", "text/plain")
        assert resp["id"] == "1"
        assert resp["name"] == "test.txt" 