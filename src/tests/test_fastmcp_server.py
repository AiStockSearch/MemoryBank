import sys
import os
import pytest
import uuid
import httpx
import asyncio
from fastapi import status
from fastapi.testclient import TestClient
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

import pytest_asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.server.api.mcp_server import app

# from src.server.api.fastmcp_api import FastMCPClient
# TODO: Реализовать или скорректировать FastMCPClient для теста
# client = FastMCPClient('http://localhost:8000')

@pytest_asyncio.fixture
def anyio_backend():
    return 'asyncio'

@pytest_asyncio.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def async_client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

from src.tests.conftest import valid_jwt_token

def valid_headers(token, user_id="test-user"):
    return {"X-API-KEY": "supersecretkey", "Authorization": f"Bearer {token}", "X-USER-ID": user_id}

@pytest.mark.anyio
async def test_export_project(async_client, valid_jwt_token):
    origin = f"test-project-export-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    resp = await async_client.post("/projects", json=data, headers=headers)
    assert resp.status_code == 200
    pid = resp.json()["project_id"]
    resp = await async_client.get(f"/projects/{pid}/export", headers=headers)
    assert resp.status_code == 200
    assert "archive_path" in resp.json()

@pytest.mark.anyio
async def test_create_task(async_client, valid_jwt_token):
    headers = valid_headers(valid_jwt_token)
    data = {"command": "test", "task_id": "t1"}
    resp = await async_client.post("/tasks", json=data, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "created"

@pytest.mark.anyio
async def test_get_backlog(async_client, valid_jwt_token):
    origin = f"test-project-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    resp = await async_client.post("/projects", json=data, headers=headers)
    assert resp.status_code == 200
    # Создаём backlog-файл
    os.makedirs(f"archive/{origin}", exist_ok=True)
    with open(f"archive/{origin}/federation_backlog.md", "w") as f:
        f.write("test backlog")
    resp = await async_client.get("/backlog", params={"origin": origin}, headers=headers)
    assert resp.status_code == 200
    assert "test backlog" in resp.text

@pytest.mark.anyio
async def test_get_context(async_client, valid_jwt_token):
    headers = valid_headers(valid_jwt_token)
    # Создаём задачу
    data = {"command": "do_something", "task_id": "t1"}
    await async_client.post("/tasks", json=data, headers=headers)
    resp = await async_client.get("/context/t1", headers=headers)
    assert resp.status_code == 200

@pytest.mark.anyio
async def test_update_rules(async_client, valid_jwt_token):
    origin = f"test-project-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    resp = await async_client.post("/projects", json=data, headers=headers)
    assert resp.status_code == 200
    # Валидный rules payload
    rules = [{"meta": {"description": "desc"}, "body": "body text"}]
    resp = await async_client.post("/rules", json={"rules": rules, "user_id": "u1"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "rules updated"

@pytest.mark.anyio
async def test_federation_pull_knowledge(async_client, valid_jwt_token):
    origin = f"test-project-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    await async_client.post("/projects", json=data, headers=headers)
    # Создаём knowledge-файл
    os.makedirs(f"archive/{origin}/knowledge_packages", exist_ok=True)
    with open(f"archive/{origin}/knowledge_packages/test.md", "w") as f:
        f.write("test knowledge")
    # GET вместо POST
    resp = await async_client.get("/federation/pull_knowledge", params={"origin": origin, "file": "test.md"}, headers=headers)
    assert resp.status_code == 200
    assert resp.content == b"test knowledge"

@pytest.mark.anyio
async def test_get_knowledge_package(async_client, valid_jwt_token):
    origin = f"test-project-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    await async_client.post("/projects", json=data, headers=headers)
    # knowledge-файл
    os.makedirs(f"archive/{origin}/knowledge_packages", exist_ok=True)
    with open(f"archive/{origin}/knowledge_packages/test.md", "w") as f:
        f.write("test knowledge")
    resp = await async_client.get("/knowledge_package", params={"origin": origin, "name": "test.md"}, headers=headers)
    assert resp.status_code == 200
    assert "test knowledge" in resp.text

@pytest.mark.anyio
async def test_get_feedback(async_client, valid_jwt_token):
    origin = f"test-project-{uuid.uuid4()}"
    headers = valid_headers(valid_jwt_token)
    data = {"name": origin, "description": "desc", "origin": origin}
    await async_client.post("/projects", json=data, headers=headers)
    # feedback-файл
    os.makedirs(f"archive/{origin}", exist_ok=True)
    with open(f"archive/{origin}/feedback.md", "w") as f:
        f.write("test feedback")
    resp = await async_client.get("/feedback", params={"origin": origin}, headers=headers)
    assert resp.status_code == 200
    assert "test feedback" in resp.text

@pytest.mark.anyio
async def test_generate_report(async_client, valid_jwt_token):
    headers = valid_headers(valid_jwt_token)
    data = {"command": "do_something", "task_id": "t1"}
    await async_client.post("/tasks", json=data, headers=headers)
    resp = await async_client.post("/generate_report", json={"context": {"task_id": "t1", "summary": "Test"}}, headers=headers)
    assert resp.status_code == 200
    assert "report" in resp.json()

# TODO: Проверь соответствие путей и параметров реальным endpoint'ам FastAPI

# Для запуска: pytest test_fastmcp_server.py 