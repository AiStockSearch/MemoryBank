import pytest
from src.services.anthropic.client import AnthropicClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_complete_success():
    client = AnthropicClient("test-key")
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value={"content": [{"text": "Ответ"}]})
        mock_post.return_value.__aenter__.return_value = mock_resp
        result = await client.complete("test prompt")
        assert "Ответ" in result

@pytest.mark.asyncio
async def test_complete_fail():
    client = AnthropicClient("test-key")
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status = 400
        mock_resp.json = AsyncMock(return_value={"error": "bad request"})
        mock_post.return_value.__aenter__.return_value = mock_resp
        result = await client.complete("test prompt")
        assert result is None 