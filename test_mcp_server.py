import pytest
from fastapi.testclient import TestClient
from mcp_server import app, API_KEY
import io
import zipfile
import tempfile
from subprocess import check_output

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

def test_batch_commit_rules(client):
    rules = [
        {"id": "ruleA", "type": "priority", "value": "high"},
        {"id": "ruleB", "type": "deadline", "value": "2025-01-01"}
    ]
    resp = client.post("/rules", json={"rules": rules}, headers={"X-USER-ID": "tester"})
    assert resp.status_code == 200
    # Проверяем, что оба файла созданы и есть в git log одним коммитом
    logA = check_output(["git", "log", "--oneline", "--", "rules/ruleA.json"]).decode()
    logB = check_output(["git", "log", "--oneline", "--", "rules/ruleB.json"]).decode()
    assert "batch-update" in logA.splitlines()[0]
    assert logA.splitlines()[0] == logB.splitlines()[0]

def test_batch_commit_templates(client):
    templates = [
        {"name": "tplA", "repo_url": "https://repo/a", "tags": ["a"]},
        {"name": "tplB", "repo_url": "https://repo/b", "tags": ["b"]}
    ]
    resp = client.post("/templates", json=templates, headers={"X-USER-ID": "tester"})
    assert resp.status_code == 200
    logA = check_output(["git", "log", "--oneline", "--", "templates/tplA.json"]).decode()
    logB = check_output(["git", "log", "--oneline", "--", "templates/tplB.json"]).decode()
    assert "batch-update" in logA.splitlines()[0]
    assert logA.splitlines()[0] == logB.splitlines()[0]

def test_rollback_rule(client):
    # Создаём правило, обновляем, откатываем
    rule = {"id": "ruleRollback", "type": "priority", "value": "low"}
    client.post("/rules", json={"rules": [rule]}, headers={"X-USER-ID": "tester"})
    rule2 = {"id": "ruleRollback", "type": "priority", "value": "high"}
    client.post("/rules", json={"rules": [rule2]}, headers={"X-USER-ID": "tester"})
    log = check_output(["git", "log", "--oneline", "--", "rules/ruleRollback.json"]).decode().splitlines()
    commit_hash = log[1].split()[0]  # первый коммит (до обновления)
    resp = client.post(f"/rules/ruleRollback/rollback", data={"commit": commit_hash}, headers={"X-USER-ID": "tester"})
    assert resp.status_code == 200
    # Проверяем, что rollback зафиксирован в истории
    log2 = check_output(["git", "log", "--oneline", "--", "rules/ruleRollback.json"]).decode()
    assert "rollback" in log2.splitlines()[0]

def test_conflict_on_rollback(client):
    # Создаём правило, обновляем, ещё раз обновляем
    rule = {"id": "ruleConflict", "type": "priority", "value": "low"}
    client.post("/rules", json={"rules": [rule]}, headers={"X-USER-ID": "tester"})
    rule2 = {"id": "ruleConflict", "type": "priority", "value": "high"}
    client.post("/rules", json={"rules": [rule2]}, headers={"X-USER-ID": "tester"})
    rule3 = {"id": "ruleConflict", "type": "priority", "value": "medium"}
    client.post("/rules", json={"rules": [rule3]}, headers={"X-USER-ID": "tester"})
    log = check_output(["git", "log", "--oneline", "--", "rules/ruleConflict.json"]).decode().splitlines()
    commit_hash = log[2].split()[0]  # первый коммит
    # Откатываем к первому коммиту
    resp = client.post(f"/rules/ruleConflict/rollback", data={"commit": commit_hash}, headers={"X-USER-ID": "tester"})
    assert resp.status_code == 200
    # Проверяем, что rollback зафиксирован
    log2 = check_output(["git", "log", "--oneline", "--", "rules/ruleConflict.json"]).decode()
    assert "rollback" in log2.splitlines()[0] 