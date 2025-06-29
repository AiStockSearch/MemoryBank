import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi.testclient import TestClient
from src.server.api.mcp_server import app
import uuid

HEADERS = {"X-API-KEY": "supersecretkey"}
client = TestClient(app)

# from src.server.api.fastmcp_api import FastMCPClient
# TODO: Реализовать или скорректировать FastMCPClient для теста
# client = FastMCPClient('http://localhost:8000')

@pytest.fixture(scope="module")
def project_id(valid_jwt_token):
    headers = {"X-API-KEY": "supersecretkey", "Authorization": f"Bearer {valid_jwt_token}"}
    # Удаляем проект с таким origin, если есть
    origin = f"test-project-{uuid.uuid4()}"
    # Пытаемся найти и удалить проект по origin
    resp = client.get(f"/projects/by_origin", params={"origin": origin}, headers=headers)
    if resp.status_code == 200:
        pid = resp.json()["project_id"]
        # Можно добавить удаление, если реализовано, иначе игнорируем
    data = {"name": origin, "description": "desc", "origin": origin}
    resp = client.post("/projects", json=data, headers=headers)
    assert resp.status_code == 200
    return resp.json()["project_id"], origin

def valid_headers(valid_jwt_token, user_id="test-user"):
    return {"X-API-KEY": "supersecretkey", "Authorization": f"Bearer {valid_jwt_token}", "X-USER-ID": user_id}

@pytest.mark.parametrize('origin', ['client-x'])
def test_export_project(origin, valid_jwt_token, project_id):
    pid, _ = project_id
    headers = valid_headers(valid_jwt_token)
    resp = client.get(f"/projects/{pid}/export", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "exported"

def test_create_task(valid_jwt_token, project_id):
    pid, origin = project_id
    headers = valid_headers(valid_jwt_token)
    data = {"command": "do_something", "task_id": "t1"}
    resp = client.post("/tasks", json=data, headers=headers)
    assert resp.status_code == 200
    assert "task" in resp.json()

def test_get_backlog(valid_jwt_token, project_id):
    _, origin = project_id
    headers = valid_headers(valid_jwt_token)
    resp = client.get("/backlog", params={"origin": origin}, headers=headers)
    assert resp.status_code == 200

def test_get_context(valid_jwt_token):
    headers = valid_headers(valid_jwt_token)
    resp = client.get("/context/t1", headers=headers)
    assert resp.status_code == 200

def test_update_rules(valid_jwt_token, project_id):
    pid, _ = project_id
    headers = valid_headers(valid_jwt_token)
    rules = [{"id": 1}]
    resp = client.post("/rules", json={"rules": rules, "user_id": "u1"}, headers=headers)
    assert resp.status_code == 200

def test_federation_pull_knowledge(valid_jwt_token, project_id):
    _, origin = project_id
    headers = valid_headers(valid_jwt_token)
    files = {'file': ('test.md', b'test content', 'text/markdown')}
    resp = client.post("/federation/pull_knowledge", data={"origin": origin}, files=files, headers=headers)
    assert resp.status_code == 200

def test_get_knowledge_package(valid_jwt_token, project_id):
    _, origin = project_id
    headers = valid_headers(valid_jwt_token)
    resp = client.get("/knowledge_package", params={"origin": origin, "name": "test.md"}, headers=headers)
    assert resp.status_code == 200

def test_get_feedback(valid_jwt_token, project_id):
    _, origin = project_id
    headers = valid_headers(valid_jwt_token)
    resp = client.get("/feedback", params={"origin": origin}, headers=headers)
    assert resp.status_code == 200

def test_generate_report(valid_jwt_token):
    headers = valid_headers(valid_jwt_token)
    resp = client.post("/generate_report", json={"context": {"task_id": "t1", "summary": "Test"}}, headers=headers)
    assert resp.status_code == 200

# TODO: Проверь соответствие путей и параметров реальным endpoint'ам FastAPI

# Для запуска: pytest test_fastmcp_server.py 