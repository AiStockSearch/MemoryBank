import pytest
from fastapi.testclient import TestClient
from mcp_server import app, API_KEY
import io
import zipfile
import tempfile
from subprocess import check_output
import os
import base64
import yaml

client = TestClient(app)

HEADERS = {"X-API-KEY": API_KEY}

RULES_DIR = ".cursor/rules"

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

def test_batch_rollback_rules(client):
    # Создаём два правила, обновляем, делаем batch rollback
    rules = [
        {"id": "ruleBR1", "type": "priority", "value": "low"},
        {"id": "ruleBR2", "type": "priority", "value": "medium"}
    ]
    client.post("/rules", json={"rules": rules}, headers={"X-USER-ID": "tester"})
    # Обновляем оба
    rules2 = [
        {"id": "ruleBR1", "type": "priority", "value": "high"},
        {"id": "ruleBR2", "type": "priority", "value": "high"}
    ]
    client.post("/rules", json={"rules": rules2}, headers={"X-USER-ID": "tester"})
    from subprocess import check_output
    log = check_output(["git", "log", "--oneline", "--", "rules/ruleBR1.json"]).decode().splitlines()
    commit_hash = log[1].split()[0]  # первый коммит (до обновления)
    # Batch rollback
    query = '''
    mutation BatchRollback($ids: [String!]!, $commit: String!, $user_id: String!) {
      batchRollbackRules(ids: $ids, commit: $commit, user_id: $user_id) {
        status
        results { ruleId status commit error }
      }
    }
    '''
    resp = client.post("/graphql", json={"query": query, "variables": {"ids": ["ruleBR1", "ruleBR2"], "commit": commit_hash, "user_id": "tester"}})
    assert resp.status_code == 200
    data = resp.json()["data"]["batchRollbackRules"]
    assert data["status"] == "ok"
    assert all(r["status"] == "rolled back" for r in data["results"])

def test_batch_delete_rules(client):
    # Создаём два правила
    rules = [
        {"id": "ruleBD1", "type": "priority", "value": "low"},
        {"id": "ruleBD2", "type": "priority", "value": "medium"}
    ]
    client.post("/rules", json={"rules": rules}, headers={"X-USER-ID": "tester"})
    # Batch delete
    query = '''
    mutation BatchDelete($ids: [String!]!, $user_id: String!) {
      batchDeleteRules(ids: $ids, user_id: $user_id) {
        status
        deletedIds
        errors
      }
    }
    '''
    resp = client.post("/graphql", json={"query": query, "variables": {"ids": ["ruleBD1", "ruleBD2"], "user_id": "tester"}})
    assert resp.status_code == 200
    data = resp.json()["data"]["batchDeleteRules"]
    assert data["status"] == "ok"
    assert set(data["deletedIds"]) == {"ruleBD1", "ruleBD2"}
    assert not data["errors"]

def test_conflict_on_import(client):
    # Импортируем проект с существующим origin
    project_id = create_test_project()
    resp = client.get(f"/projects/{project_id}/export", headers=HEADERS)
    assert resp.status_code == 200
    zip_bytes = resp.content
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        data = {"new_origin": "test-origin"}  # origin уже существует
        resp2 = client.post("/projects/import", files=files, data=data, headers=HEADERS)
        assert resp2.status_code == 409
        # Здесь можно проверить, что notify_conflict был вызван (например, через mock или лог)

def test_conflict_on_merge(client):
    # Создаём проект, экспортируем, импортируем, делаем merge с конфликтом
    project_id = create_test_project()
    client.post("/tasks", json={"command": "cmd", "task_id": "t1"}, headers=HEADERS)
    resp = client.get(f"/projects/{project_id}/export", headers=HEADERS)
    zip_bytes = resp.content
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        data = {"new_origin": "imported-origin"}
        resp2 = client.post("/projects/import", files=files, data=data, headers=HEADERS)
        imported_id = resp2.json()["project_id"]
    # Добавляем задачу с тем же id в импортированный проект
    client.post("/tasks", json={"command": "cmd2", "task_id": "t1"}, headers=HEADERS)
    # Merge с конфликтом
    with tempfile.NamedTemporaryFile(suffix='.zip') as tmp:
        tmp.write(zip_bytes)
        tmp.seek(0)
        files = {"file": ("export.zip", tmp, "application/zip")}
        resp3 = client.post(f"/projects/{imported_id}/merge", files=files, data={"dry_run": "true"}, headers=HEADERS)
        assert resp3.status_code == 200
        diff = resp3.json()
        assert diff["tasks"]["conflicted"]
        # Здесь можно проверить, что notify_conflict был вызван (например, через mock или лог)

def test_batch_rollback_templates(client):
    # Создаём два шаблона, обновляем, делаем batch rollback
    templates = [
        {"name": "tplBR1", "repo_url": "https://repo/a", "tags": ["a"]},
        {"name": "tplBR2", "repo_url": "https://repo/b", "tags": ["b"]}
    ]
    client.post("/templates", json=templates, headers={"X-USER-ID": "tester"})
    # Обновляем оба
    templates2 = [
        {"name": "tplBR1", "repo_url": "https://repo/a2", "tags": ["a2"]},
        {"name": "tplBR2", "repo_url": "https://repo/b2", "tags": ["b2"]}
    ]
    client.post("/templates", json=templates2, headers={"X-USER-ID": "tester"})
    from subprocess import check_output
    log = check_output(["git", "log", "--oneline", "--", "templates/tplBR1.json"]).decode().splitlines()
    commit_hash = log[1].split()[0]  # первый коммит (до обновления)
    # Batch rollback
    query = '''
    mutation BatchRollback($names: [String!]!, $commit: String!, $user_id: String!) {
      batchRollbackTemplates(names: $names, commit: $commit, user_id: $user_id) {
        status
        results { ruleId status commit error }
      }
    }
    '''
    resp = client.post("/graphql", json={"query": query, "variables": {"names": ["tplBR1", "tplBR2"], "commit": commit_hash, "user_id": "tester"}})
    assert resp.status_code == 200
    data = resp.json()["data"]["batchRollbackTemplates"]
    assert data["status"] == "ok"
    assert all(r["status"] == "rolled back" for r in data["results"])

def test_batch_delete_templates(client):
    # Создаём два шаблона
    templates = [
        {"name": "tplBD1", "repo_url": "https://repo/a", "tags": ["a"]},
        {"name": "tplBD2", "repo_url": "https://repo/b", "tags": ["b"]}
    ]
    client.post("/templates", json=templates, headers={"X-USER-ID": "tester"})
    # Batch delete
    query = '''
    mutation BatchDelete($names: [String!]!, $user_id: String!) {
      batchDeleteTemplates(names: $names, user_id: $user_id) {
        status
        deletedIds
        errors
      }
    }
    '''
    resp = client.post("/graphql", json={"query": query, "variables": {"names": ["tplBD1", "tplBD2"], "user_id": "tester"}})
    assert resp.status_code == 200
    data = resp.json()["data"]["batchDeleteTemplates"]
    assert data["status"] == "ok"
    assert set(data["deletedIds"]) == {"tplBD1", "tplBD2"}
    assert not data["errors"]

def test_rules_crud():
    # 1. Создать правило
    rule = {
        "meta": {"description": "test rule", "alwaysApply": True},
        "body": "- test body"
    }
    resp = client.post("/rules", json={"rules": [rule]}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rules updated"
    path = data["results"][0]["path"]
    # 2. Получить список правил
    resp = client.get("/rules", headers=HEADERS)
    assert resp.status_code == 200
    rules = resp.json()
    assert any(r["meta"]["description"] == "test rule" for r in rules)
    # 3. Удалить правило
    resp = client.delete("/rules", params={"path": path}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

def test_rules_export_import():
    # Создать несколько правил
    rule1 = {"meta": {"description": "rule1"}, "body": "- body1"}
    rule2 = {"meta": {"description": "rule2"}, "body": "- body2"}
    client.post("/rules", json={"rules": [rule1, rule2]}, headers=HEADERS)
    # Экспортировать zip
    resp = client.get("/rules/export", headers=HEADERS)
    assert resp.status_code == 200
    zip_bytes = resp.content
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zipf:
        names = zipf.namelist()
        assert any(n.endswith(".mdc") for n in names)
    # Удалить все правила
    rules = client.get("/rules", headers=HEADERS).json()
    for r in rules:
        client.delete("/rules", params={"path": r["path"]}, headers=HEADERS)
    # Импортировать zip
    resp = client.post("/rules/import", files={"file": ("rules.zip", zip_bytes)}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "imported"
    # Проверить, что правила восстановились
    rules = client.get("/rules", headers=HEADERS).json()
    assert any(r["meta"]["description"] == "rule1" for r in rules)
    assert any(r["meta"]["description"] == "rule2" for r in rules)
    # Очистить
    for r in rules:
        client.delete("/rules", params={"path": r["path"]}, headers=HEADERS)

def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = client.post("/graphql", json=payload)
    return resp

def test_graphql_mdc_rules_crud():
    # 1. Создать правило
    mutation = '''
    mutation Create($input: RuleMDCInput!, $userId: String!) {
      createRuleMdc(input: $input, userId: $userId) { path meta body }
    }
    '''
    variables = {"input": {"meta": {"description": "gql rule", "alwaysApply": True}, "body": "- gql body", "filename": "gql_rule.mdc"}, "userId": "tester"}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    path = resp.json()["data"]["createRuleMdc"]["path"]
    # 2. Получить список правил
    query = """
    query { rulesMdc { path meta body } }
    """
    resp = gql(query)
    assert resp.status_code == 200
    rules = resp.json()["data"]["rulesMdc"]
    assert any(r["meta"]["description"] == "gql rule" for r in rules)
    # 3. Получить одно правило
    query = """
    query Get($path: String!) { ruleMdc(path: $path) { meta body path } }
    """
    resp = gql(query, {"path": path})
    assert resp.status_code == 200
    assert resp.json()["data"]["ruleMdc"]["meta"]["description"] == "gql rule"
    # 4. Обновить правило
    mutation = '''
    mutation Update($input: RuleMDCInput!, $userId: String!) {
      updateRuleMdc(input: $input, userId: $userId) { path meta body }
    }
    '''
    variables = {"input": {"path": path, "meta": {"description": "gql rule updated"}, "body": "- updated"}, "userId": "tester"}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    assert resp.json()["data"]["updateRuleMdc"]["meta"]["description"] == "gql rule updated"
    # 5. Changelog
    query = """
    query Get($path: String!) { changelogMdc(path: $path) { commit author date message } }
    """
    resp = gql(query, {"path": path})
    assert resp.status_code == 200
    assert resp.json()["data"]["changelogMdc"]
    # 6. Экспортировать zip
    mutation = """
    mutation { exportRulesMdc }
    """
    resp = gql(mutation)
    assert resp.status_code == 200
    zip_b64 = resp.json()["data"]["exportRulesMdc"]
    zip_bytes = base64.b64decode(zip_b64)
    # 7. Удалить правило
    mutation = '''
    mutation Delete($path: String!, $userId: String!) {
      deleteRuleMdc(path: $path, userId: $userId)
    }
    '''
    resp = gql(mutation, {"path": path, "userId": "tester"})
    assert resp.status_code == 200
    # 8. Импортировать zip
    mutation = '''
    mutation Import($fileB64: String!, $userId: String!) {
      importRulesMdc(fileB64: $fileB64, userId: $userId)
    }
    '''
    resp = gql(mutation, {"fileB64": base64.b64encode(zip_bytes).decode(), "userId": "tester"})
    assert resp.status_code == 200
    # 9. Проверить, что правило восстановилось
    query = """
    query { rulesMdc { path meta body } }
    """
    resp = gql(query)
    assert resp.status_code == 200
    assert any(r["meta"]["description"] == "gql rule updated" for r in resp.json()["data"]["rulesMdc"])
    # 10. Rollback (если есть хотя бы 2 коммита)
    changelog = gql("query Get($path: String!) { changelogMdc(path: $path) { commit } }", {"path": path}).json()["data"]["changelogMdc"]
    if len(changelog) > 1:
        old_commit = changelog[-1]["commit"]
        mutation = '''
        mutation Rollback($path: String!, $commit: String!, $userId: String!) {
          rollbackRuleMdc(path: $path, commit: $commit, userId: $userId)
        }
        '''
        resp = gql(mutation, {"path": path, "commit": old_commit, "userId": "tester"})
        assert resp.status_code == 200

def test_memory_bank_import_export():
    # Создаём временный архив memory-bank
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test123')
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w') as zf:
            zf.write(test_file, 'test.txt')
        mem_zip.seek(0)
        # Импорт
        resp = client.post('/memory-bank/import', files={'file': ('memory-bank.zip', mem_zip, 'application/zip')})
        assert resp.status_code == 200
        assert resp.json()['status'] == 'imported'
        # Экспорт
        resp2 = client.get('/memory-bank/export')
        assert resp2.status_code == 200
        with zipfile.ZipFile(io.BytesIO(resp2.content)) as zf:
            assert 'test.txt' in zf.namelist()

def test_memory_bank_merge_and_rollback():
    # Создаём архив с новым файлом
    with tempfile.TemporaryDirectory() as tmpdir:
        new_file = os.path.join(tmpdir, 'new.txt')
        with open(new_file, 'w') as f:
            f.write('newdata')
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w') as zf:
            zf.write(new_file, 'new.txt')
        mem_zip.seek(0)
        # Merge dry-run
        resp = client.post('/memory-bank/merge', files={'archive': ('merge.zip', mem_zip, 'application/zip')}, data={'dry_run': 'true'})
        assert resp.status_code == 200
        assert 'NEW: new.txt' in resp.json()['diff']
        # Merge реальный
        mem_zip.seek(0)
        resp2 = client.post('/memory-bank/merge', files={'archive': ('merge.zip', mem_zip, 'application/zip')}, data={'dry_run': 'false'})
        assert resp2.status_code == 200
        assert resp2.json()['status'] == 'merged'
        # Rollback (откат к этому архиву)
        mem_zip.seek(0)
        resp3 = client.post('/memory-bank/rollback', files={'snapshot': ('rollback.zip', mem_zip, 'application/zip')})
        assert resp3.status_code == 200
        assert resp3.json()['status'] == 'rolled back'

def test_memory_bank_batch():
    # Архив с двумя файлами
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, 'a.txt')
        f2 = os.path.join(tmpdir, 'b.txt')
        with open(f1, 'w') as f:
            f.write('A')
        with open(f2, 'w') as f:
            f.write('B')
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, 'w') as zf:
            zf.write(f1, 'a.txt')
            zf.write(f2, 'b.txt')
        mem_zip.seek(0)
        resp = client.post('/memory-bank/batch', files={'batch': ('batch.zip', mem_zip, 'application/zip')})
        assert resp.status_code == 200
        assert 'a.txt' in resp.json()['files']
        assert 'b.txt' in resp.json()['files']

def test_memory_bank_federation():
    # Push knowledge package
    content = b'knowledge123'
    resp = client.post('/memory-bank/federation/push', files={'file': ('test-knowledge.md', io.BytesIO(content), 'text/markdown')})
    assert resp.status_code == 200
    assert resp.json()['status'] == 'uploaded'
    # Pull knowledge package
    resp2 = client.get('/memory-bank/federation/pull', params={'file': 'test-knowledge.md'})
    assert resp2.status_code == 200
    assert resp2.content == content

def test_custom_command():
    assert resp2.content == content

def test_custom_command_action():
    import yaml
    # Создаём временный custom command YAML с action: echo_action
    os.makedirs('memory-bank/custom_commands', exist_ok=True)
    cmd_yaml = {
        'name': 'echo',
        'description': 'Echo test command',
        'parameters': [{'name': 'msg', 'type': 'string', 'required': True}],
        'action': 'echo_action'
    }
    with open('memory-bank/custom_commands/echo.yaml', 'w') as f:
        yaml.dump(cmd_yaml, f)
    params = {'msg': 'hello world'}
    resp = client.post('/custom_command/echo', json=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data['command'] == 'echo'
    assert data['description'] == 'Echo test command'
    assert data['parameters'] == params
    assert data['action'] == 'echo_action'
    assert data['result'] == {'echo': 'hello world'}

def test_analyze_changelog_command():
    # Создаём CHANGELOG.md с примерами
    os.makedirs('memory-bank', exist_ok=True)
    with open('memory-bank/CHANGELOG.md', 'w') as f:
        f.write('[2024-06-20] fix: Исправлен баг\n[2024-06-21] feat: Новая фича\n[2024-06-22] error: Ошибка\n')
    resp = client.post('/custom_command/analyze_changelog', json={})
    assert resp.status_code == 200
    data = resp.json()['result']
    assert 'fix:' in ''.join(data['anomalies'])
    assert 'feat:' in ''.join(data['summary'])

def test_generate_best_practices_command():
    # Создаём systemPatterns.md с секцией Best practices
    with open('memory-bank/systemPatterns.md', 'w') as f:
        f.write('# systemPatterns\n\n## Best practices\n- Использовать DRY\n- Писать тесты\n')
    resp = client.post('/custom_command/generate_best_practices', json={})
    assert resp.status_code == 200
    data = resp.json()['result']
    assert any('DRY' in p for p in data['best_practices'])

def test_ai_review_changes_command():
    # CHANGELOG.md уже создан выше
    resp = client.post('/custom_command/ai_review_changes', json={})
    assert resp.status_code == 200
    data = resp.json()['result']
    assert isinstance(data['improvements'], list)
    assert isinstance(data['risks'], list) 