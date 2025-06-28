import pytest
from fastapi.testclient import TestClient
from mcp_server import app, API_KEY
import io
import zipfile
import tempfile

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

def create_test_project():
    resp = client.post("/projects", json={"name": "TestProj", "description": "desc", "origin": "test-origin"})
    assert resp.status_code == 200
    return resp.json()["project_id"]

def test_export_import_merge():
    # 1. Создаём проект и задачу
    project_id = create_test_project()
    client.post("/tasks", json={"command": "cmd", "task_id": "t1"}, headers=HEADERS)
    # 2. Экспортируем проект
    resp = client.get(f"/projects/{project_id}/export", headers=HEADERS)
    assert resp.status_code == 200
    zip_bytes = resp.content
    # 3. Импортируем как новый проект (с новым origin)
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        data = {"new_origin": "imported-origin"}
        resp2 = client.post("/projects/import", files=files, data=data, headers=HEADERS)
        assert resp2.status_code == 200
        imported = resp2.json()
        assert imported["status"] == "imported"
        imported_id = imported["project_id"]
    # 4. Merge dry-run (diff)
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        resp3 = client.post(f"/projects/{imported_id}/merge", files=files, data={"dry_run": "true"}, headers=HEADERS)
        assert resp3.status_code == 200
        diff = resp3.json()
        assert "tasks" in diff and "added" in diff["tasks"]
    # 5. Merge реальный (ничего не должно добавиться, всё уже есть)
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        resp4 = client.post(f"/projects/{imported_id}/merge", files=files, data={"dry_run": "false"}, headers=HEADERS)
        assert resp4.status_code == 200
        merged = resp4.json()
        assert merged["status"] == "merged"
        # После merge ничего не добавлено
        assert all(v == 0 for v in merged["added"].values() if isinstance(v, int)) 