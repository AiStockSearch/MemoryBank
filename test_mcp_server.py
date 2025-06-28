import pytest
from fastapi.testclient import TestClient
from mcp_server import app, API_KEY

client = TestClient(app)

HEADERS = {"X-API-KEY": API_KEY}

def test_create_task():
    response = client.post("/tasks", json={"command": "test_cmd", "task_id": "test1"}, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["task"]["id"] == "test1"

def test_get_context_not_found():
    response = client.get("/context/unknown_task", headers=HEADERS)
    assert response.status_code == 404

def test_update_rules():
    rules = [{"id": "ruleX", "type": "priority", "value": "high"}]
    response = client.post("/rules", json={"rules": rules}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "rules updated" 