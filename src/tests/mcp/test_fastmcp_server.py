import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
def test_healthcheck():
    """
    Проверка доступности healthcheck эндпоинта (если реализован).
    """
    async def run():
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/health")
            assert resp.status_code == 200
            assert resp.json().get("status") in ("ok", "healthy")
    import asyncio
    asyncio.run(run())

@pytest.mark.asyncio
def test_llm_generate():
    """
    Проверка работы LLM-эндпоинта (пример для FastMCP).
    """
    llm_payload = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "prompt": "Test prompt",
        "params": {"max_tokens": 10}
    }
    headers = {
        "X-API-KEY": "supersecretkey",
        "Authorization": "Bearer testjwt"
    }
    async def run():
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{BASE_URL}/api/llm/generate", json=llm_payload, headers=headers)
            assert resp.status_code in (200, 400, 401)
    import asyncio
    asyncio.run(run())

@pytest.mark.asyncio
def test_ws_events():
    """
    Проверка работы WebSocket-эндпоинта (если реализован).
    """
    import websockets
    import json
    async def run():
        uri = f"ws://localhost:8000/api/ws/events"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"cmd": "ping"}))
            response = await ws.recv()
            assert "pong" in response or "result" in response
    import asyncio
    asyncio.run(run()) 