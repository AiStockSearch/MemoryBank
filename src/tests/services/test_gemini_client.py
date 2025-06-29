import pytest
from src.services.gemini.client import GeminiClient
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_complete_success():
    client = GeminiClient("test-key")
    with patch("aiohttp.ClientSession", new_callable=AsyncMock) as mock_session:
        mock_session_instance = mock_session.return_value.__aenter__.return_value
        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__.return_value.status = 200
        mock_post_ctx.__aenter__.return_value.json = AsyncMock(return_value={
            "candidates": [{"content": {"parts": [{"text": "Ответ Gemini"}]}}]
        })
        mock_session_instance.post.return_value = mock_post_ctx
        result = await client.complete("test prompt")
        assert "Ответ Gemini" in result

@pytest.mark.asyncio
async def test_complete_fail():
    client = GeminiClient("test-key")
    with patch("aiohttp.ClientSession", new_callable=AsyncMock) as mock_session:
        mock_session_instance = mock_session.return_value.__aenter__.return_value
        mock_post_ctx = AsyncMock()
        mock_post_ctx.__aenter__.return_value.status = 400
        mock_post_ctx.__aenter__.return_value.json = AsyncMock(return_value={"error": "bad request"})
        mock_session_instance.post.return_value = mock_post_ctx
        result = await client.complete("test prompt")
        assert result is None 