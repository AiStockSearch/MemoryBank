import pytest
from src.services.local_llm.client import LocalLLMClient
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
async def test_complete_ollama():
    client = LocalLLMClient("http://localhost:11434")
    response = MockResponse(200, {"choices": [{"text": "Ответ Ollama"}]})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert "Ответ Ollama" in result

@pytest.mark.asyncio
async def test_complete_lm_studio():
    client = LocalLLMClient("http://localhost:1234")
    response = MockResponse(200, {"choices": [{"message": {"content": "Ответ LM Studio"}}]})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert "Ответ LM Studio" in result

@pytest.mark.asyncio
async def test_complete_hf_inference():
    client = LocalLLMClient("http://localhost:8000")
    response = MockResponse(200, {"generated_text": "Ответ HF"})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert "Ответ HF" in result

@pytest.mark.asyncio
async def test_complete_fail():
    client = LocalLLMClient("http://localhost:11434")
    response = MockResponse(400, {"error": "bad request"})
    with patch("aiohttp.ClientSession", return_value=MockSession(response)):
        result = await client.complete("test prompt")
        assert result is None 