import pytest
import aiohttp
from src.services.confluence.client import ConfluenceClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_get_page_success():
    client = ConfluenceClient("https://test.atlassian.net/wiki", "token")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"id": "123", "title": "Test"})
        mock_get.return_value.__aenter__.return_value = mock_resp
        page = await client.get_page("123")
        assert page["id"] == "123"
        assert page["title"] == "Test"

@pytest.mark.asyncio
async def test_get_page_not_found():
    client = ConfluenceClient("https://test.atlassian.net/wiki", "token")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_get.return_value.__aenter__.return_value = mock_resp
        page = await client.get_page("notfound")
        assert page is None

@pytest.mark.asyncio
async def test_create_page_success():
    client = ConfluenceClient("https://test.atlassian.net/wiki", "token")
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 201
        mock_resp.json = AsyncMock(return_value={"id": "456", "title": "Created"})
        mock_post.return_value.__aenter__.return_value = mock_resp
        page = await client.create_page("DEV", "Created", "<h1>Body</h1>")
        assert page["id"] == "456"
        assert page["title"] == "Created"

@pytest.mark.asyncio
async def test_search_pages_success():
    client = ConfluenceClient("https://test.atlassian.net/wiki", "token")
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"results": [{"id": "1"}, {"id": "2"}]})
        mock_get.return_value.__aenter__.return_value = mock_resp
        results = await client.search_pages("type=page")
        assert len(results) == 2
        assert results[0]["id"] == "1" 