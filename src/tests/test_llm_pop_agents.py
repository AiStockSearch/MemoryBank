import os
os.environ["OPENAI_API_KEY"] = "test-key"
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from src.server.api.mcp_server import app
from src.tests.conftest import valid_jwt_token
import json
import websockets
import asyncio
from unittest.mock import patch

def valid_headers(token, user_id="test-user"):
    return {"X-API-KEY": "supersecretkey", "Authorization": f"Bearer {token}", "X-USER-ID": user_id}

@pytest.mark.anyio
@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch('src.services.openai.client.call_openai', return_value="Привет!")
async def test_llm_openai_generate(mock_call_openai, async_client, valid_jwt_token):
    """
    Проверяет генерацию текста через REST endpoint LLM-агента (OpenAI), с моканым call_openai и подменой переменной окружения.
    """
    headers = valid_headers(valid_jwt_token)
    data = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "prompt": "Say hello in Russian",
        "params": {"max_tokens": 10}
    }
    resp = await async_client.post("/api/llm/generate", json=data, headers=headers)
    if resp.status_code != 200:
        print("REST LLM error:", resp.text)
    assert resp.status_code == 200
    assert "привет" in resp.json().get("result", "").lower()

@pytest.mark.asyncio
@patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
@patch('src.services.openai.client.call_openai', return_value="Привет!")
async def test_llm_openai_websocket(mock_call_openai, valid_jwt_token):
    """
    Проверяет генерацию текста через WebSocket POP-агента (cmd: openai), с моканым call_openai и подменой переменной окружения.
    """
    token = valid_jwt_token
    api_key = "supersecretkey"
    uri = f"ws://localhost:8000/api/ws/events?token={token}&api_key={api_key}"
    async with websockets.connect(uri) as ws:
        msg = {
            "cmd": "openai",
            "prompt": "Say hello in Russian",
            "model": "gpt-3.5-turbo",
            "max_tokens": 10
        }
        await ws.send(json.dumps(msg))
        response = await ws.recv()
        data = json.loads(response)
        assert "result" in data
        assert "привет" in data["result"].lower()

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac 