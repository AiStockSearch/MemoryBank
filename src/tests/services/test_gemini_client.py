import pytest
from src.services.gemini.client import GeminiClient
from unittest.mock import patch

class MockResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json = json_data
    async def json(self):
        return self._json
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

class MockSession:
    def __init__(self, response):
        self._response = response
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    def post(self, *args, **kwargs):
        return self._response

@pytest.mark.asyncio
async def test_complete_success():
    client = GeminiClient("test-key")
    response = MockResponse(200, {"candidates": [{"content": {"parts": [{"text": "Ответ Gemini"}]}}]})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert "Ответ Gemini" in result

@pytest.mark.asyncio
async def test_complete_fail():
    client = GeminiClient("test-key")
    response = MockResponse(400, {"error": "bad request"})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert result is None 