import pytest
import httpx
import asyncio

@pytest.mark.asyncio
async def test_llm_question_to_rest_response():
    user_question = "Сгенерируй summary по задаче: Сделать интеграцию с Jira"
    llm_payload = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "prompt": f"Summarize: {user_question}",
        "params": {"max_tokens": 50}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8000/api/llm/generate",
            json=llm_payload,
            headers={"X-API-KEY": "supersecretkey", "Authorization": "Bearer testjwt"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data or "result" in data

@pytest.mark.asyncio
async def test_llm_question_to_pop_response():
    import websockets
    user_question = "Сделай summary по тексту: MCP интеграция"
    llm_ws_payload = {
        "cmd": "openai",
        "prompt": user_question,
        "model": "gpt-3.5-turbo"
    }
    async with websockets.connect("ws://localhost:8000/api/ws/events") as ws:
        import json
        await ws.send(json.dumps(llm_ws_payload))
        response = await ws.recv()
        assert "summary" in response or "result" in response

@pytest.mark.asyncio
async def test_llm_invalid_prompt():
    llm_payload = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "prompt": "",
        "params": {"max_tokens": 10}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8000/api/llm/generate",
            json=llm_payload,
            headers={"X-API-KEY": "supersecretkey", "Authorization": "Bearer testjwt"}
        )
    assert resp.status_code in (400, 422)

@pytest.mark.asyncio
async def test_llm_unsupported_model():
    llm_payload = {
        "provider": "openai",
        "model": "nonexistent-model",
        "prompt": "Test prompt",
        "params": {"max_tokens": 10}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8000/api/llm/generate",
            json=llm_payload,
            headers={"X-API-KEY": "supersecretkey", "Authorization": "Bearer testjwt"}
        )
    assert resp.status_code in (400, 422, 500)
    data = resp.json()
    assert "error" in data or "message" in data

@pytest.mark.asyncio
async def test_llm_broadcast_websocket():
    import websockets
    import json
    user_question = "Broadcast: Проверьте интеграцию LLM"
    llm_ws_payload = {
        "cmd": "broadcast",
        "prompt": user_question,
        "model": "gpt-3.5-turbo"
    }
    # Эмулируем подключение нескольких агентов
    async def agent():
        async with websockets.connect("ws://localhost:8000/api/ws/events") as ws:
            await ws.send(json.dumps(llm_ws_payload))
            response = await ws.recv()
            assert "broadcast" in response or "result" in response
    await asyncio.gather(agent(), agent())

@pytest.mark.asyncio
async def test_llm_chain_of_agents():
    # Эмулируем цепочку: генерация → анализ → публикация (моки)
    # Здесь просто проверяем, что MCP поддерживает последовательные вызовы
    user_question = "Сделай summary, проанализируй и опубликуй результат"
    llm_payloads = [
        {"provider": "openai", "model": "gpt-3.5-turbo", "prompt": f"Summarize: {user_question}", "params": {"max_tokens": 30}},
        {"provider": "openai", "model": "gpt-3.5-turbo", "prompt": "Analyze: summary", "params": {"max_tokens": 30}},
        {"provider": "openai", "model": "gpt-3.5-turbo", "prompt": "Publish: analysis", "params": {"max_tokens": 30}},
    ]
    async with httpx.AsyncClient() as client:
        for payload in llm_payloads:
            resp = await client.post(
                "http://localhost:8000/api/llm/generate",
                json=payload,
                headers={"X-API-KEY": "supersecretkey", "Authorization": "Bearer testjwt"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "result" in data or "summary" in data or "analysis" in data

@pytest.mark.asyncio
async def test_llm_load_many_parallel():
    # Проверка нагрузки: много параллельных запросов
    async def single_request():
        llm_payload = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "prompt": "Test load",
            "params": {"max_tokens": 5}
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8000/api/llm/generate",
                json=llm_payload,
                headers={"X-API-KEY": "supersecretkey", "Authorization": "Bearer testjwt"}
            )
            assert resp.status_code == 200
    await asyncio.gather(*(single_request() for _ in range(10)))

@pytest.mark.asyncio
async def test_llm_integration_with_taskagent(monkeypatch):
    from src.mcp.agents.business.task_agent import TaskAgent
    class MockClient:
        async def create_task(self, *a, **kw):
            return {"status": "ok", "task_id": "T-1"}
    agent = TaskAgent(jira=MockClient())
    payload = {"action": "create_task", "service": "jira", "project": "DEMO", "summary": "Test", "description": "Desc"}
    result = await agent.handle_pop(payload)
    assert result["status"] == "ok"
    assert result["task_id"] == "T-1"

@pytest.mark.asyncio
async def test_llm_integration_with_feedbackagent(monkeypatch):
    from src.mcp.agents.business.feedback_agent import FeedbackAgent
    class MockClient:
        async def submit_feedback(self, *a, **kw):
            return {"status": "ok", "feedback": {"user": "user1"}}
    agent = FeedbackAgent(MockClient())
    payload = {"action": "submit_feedback", "user": "user1", "text": "Test!"}
    result = await agent.handle_pop(payload)
    assert result["status"] == "ok"
    assert result["feedback"]["user"] == "user1"

@pytest.mark.asyncio
async def test_llm_integration_with_biagent(monkeypatch):
    from src.mcp.agents.business.bi_agent import BIAgent
    class MockClient:
        async def send_data(self, data):
            return {"status": "ok", "rows": len(data)}
    agent = BIAgent(MockClient())
    payload = {"action": "send_data", "data": [{"date": "2024-07-01", "users": 100, "sales": 2000}]}
    result = await agent.handle_pop(payload)
    assert result["status"] == "ok"
    assert result["rows"] == 1 