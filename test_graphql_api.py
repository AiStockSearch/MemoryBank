import pytest
from fastapi.testclient import TestClient
from mcp_server import app
import json
import threading
import time
import websocket
import json as js

client = TestClient(app)

GRAPHQL_URL = "/graphql"
API_KEY = "supersecretkey"

# Helper for GraphQL requests
def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = client.post(GRAPHQL_URL, json=payload, headers={"X-API-KEY": API_KEY})
    return resp

def test_projects_query():
    query = """
    query { projects { id name description origin } }
    """
    resp = gql(query)
    assert resp.status_code == 200
    assert "projects" in resp.json()["data"]

def test_create_and_update_task():
    # Create
    mutation = """
    mutation CreateTask($input: TaskInput!) {
      createTask(input: $input) { id command status }
    }
    """
    variables = {"input": {"projectId": 1, "id": "gqltest1", "command": "cmd", "status": "new"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    assert resp.json()["data"]["createTask"]["id"] == "gqltest1"
    # Update
    mutation2 = """
    mutation UpdateTask($id: String!, $input: TaskUpdateInput!) {
      updateTask(id: $id, input: $input) { id status result }
    }
    """
    variables2 = {"id": "gqltest1", "input": {"status": "done", "result": "ok"}}
    resp2 = gql(mutation2, variables2)
    assert resp2.status_code == 200
    assert resp2.json()["data"]["updateTask"]["status"] == "done"
    # Delete
    mutation3 = """
    mutation DeleteTask($id: String!) {
      deleteTask(id: $id)
    }
    """
    variables3 = {"id": "gqltest1"}
    resp3 = gql(mutation3, variables3)
    assert resp3.status_code == 200
    assert resp3.json()["data"]["deleteTask"] is True

def test_create_and_update_doc():
    # Create
    mutation = """
    mutation CreateDoc($input: DocInput!) {
      createDoc(input: $input) { id type content }
    }
    """
    variables = {"input": {"projectId": 1, "type": "spec", "content": "test doc"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    doc_id = resp.json()["data"]["createDoc"]["id"]
    # Update
    mutation2 = """
    mutation UpdateDoc($id: Int!, $input: DocUpdateInput!) {
      updateDoc(id: $id, input: $input) { id type content }
    }
    """
    variables2 = {"id": int(doc_id), "input": {"content": "updated doc"}}
    resp2 = gql(mutation2, variables2)
    assert resp2.status_code == 200
    assert resp2.json()["data"]["updateDoc"]["content"] == "updated doc"
    # Delete
    mutation3 = """
    mutation DeleteDoc($id: Int!) {
      deleteDoc(id: $id)
    }
    """
    variables3 = {"id": int(doc_id)}
    resp3 = gql(mutation3, variables3)
    assert resp3.status_code == 200
    assert resp3.json()["data"]["deleteDoc"] is True

def test_create_and_update_rule():
    # Create
    mutation = """
    mutation { updateRule(id: "rule1", input: { value: "high" }) { id value } }
    """
    # Предполагается, что rule1 уже есть (или добавить создание)
    resp = gql(mutation)
    assert resp.status_code == 200
    # Delete
    mutation2 = """
    mutation { deleteRule(id: "rule1") }
    """
    resp2 = gql(mutation2)
    assert resp2.status_code == 200

def test_create_and_update_template():
    # Create
    mutation = """
    mutation { updateTemplate(id: 1, input: { name: "tplX" }) { id name } }
    """
    # Предполагается, что шаблон с id=1 уже есть (или добавить создание)
    resp = gql(mutation)
    assert resp.status_code == 200
    # Delete
    mutation2 = """
    mutation { deleteTemplate(id: 1) }
    """
    resp2 = gql(mutation2)
    assert resp2.status_code == 200

# Тест подписки на обновление задачи
def test_subscription_on_task_update():
    # Для теста подписки нужен отдельный поток
    results = []
    def ws_thread():
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8001/graphql", subprotocols=["graphql-transport-ws"], header=["X-API-KEY: supersecretkey"])
        ws.send(js.dumps({"type": "connection_init", "payload": {}}))
        ws.send(js.dumps({
            "id": "1",
            "type": "subscribe",
            "payload": {
                "query": "subscription($projectId: Int!) { onTaskUpdate(projectId: $projectId) { id status } }",
                "variables": {"projectId": 1}
            }
        }))
        for _ in range(2):
            msg = ws.recv()
            results.append(msg)
        ws.close()
    t = threading.Thread(target=ws_thread)
    t.start()
    time.sleep(1)
    # Триггерим обновление задачи
    mutation = """
    mutation UpdateTask($id: String!, $input: TaskUpdateInput!) {
      updateTask(id: $id, input: $input) { id status }
    }
    """
    variables = {"id": "gqltest1", "input": {"status": "in_progress"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    t.join(timeout=5)
    assert any("in_progress" in m for m in results)

def test_subscription_on_doc_update():
    results = []
    def ws_thread():
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8001/graphql", subprotocols=["graphql-transport-ws"], header=["X-API-KEY: supersecretkey"])
        ws.send(js.dumps({"type": "connection_init", "payload": {}}))
        ws.send(js.dumps({
            "id": "1",
            "type": "subscribe",
            "payload": {
                "query": "subscription($projectId: Int!) { onDocUpdate(projectId: $projectId) { id content } }",
                "variables": {"projectId": 1}
            }
        }))
        for _ in range(2):
            msg = ws.recv()
            results.append(msg)
        ws.close()
    t = threading.Thread(target=ws_thread)
    t.start()
    time.sleep(1)
    # Триггерим обновление документа
    mutation = """
    mutation CreateDoc($input: DocInput!) {
      createDoc(input: $input) { id content }
    }
    """
    variables = {"input": {"projectId": 1, "type": "spec", "content": "doc_live_test"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    t.join(timeout=5)
    assert any("doc_live_test" in m for m in results)

def test_subscription_on_rule_update():
    results = []
    def ws_thread():
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8001/graphql", subprotocols=["graphql-transport-ws"], header=["X-API-KEY: supersecretkey"])
        ws.send(js.dumps({"type": "connection_init", "payload": {}}))
        ws.send(js.dumps({
            "id": "1",
            "type": "subscribe",
            "payload": {
                "query": "subscription($projectId: Int!) { onRuleUpdate(projectId: $projectId) { id value } }",
                "variables": {"projectId": 1}
            }
        }))
        for _ in range(2):
            msg = ws.recv()
            results.append(msg)
        ws.close()
    t = threading.Thread(target=ws_thread)
    t.start()
    time.sleep(1)
    # Триггерим обновление правила
    mutation = """
    mutation CreateRule($input: RuleInput!) {
      createRule(input: $input) { id value }
    }
    """
    variables = {"input": {"projectId": 1, "id": "rule_live_test", "type": "priority", "value": "high"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    t.join(timeout=5)
    assert any("rule_live_test" in m for m in results)

def test_subscription_on_template_update():
    results = []
    def ws_thread():
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8001/graphql", subprotocols=["graphql-transport-ws"], header=["X-API-KEY: supersecretkey"])
        ws.send(js.dumps({"type": "connection_init", "payload": {}}))
        ws.send(js.dumps({
            "id": "1",
            "type": "subscribe",
            "payload": {
                "query": "subscription($projectId: Int!) { onTemplateUpdate(projectId: $projectId) { id name } }",
                "variables": {"projectId": 1}
            }
        }))
        for _ in range(2):
            msg = ws.recv()
            results.append(msg)
        ws.close()
    t = threading.Thread(target=ws_thread)
    t.start()
    time.sleep(1)
    # Триггерим обновление шаблона
    mutation = """
    mutation CreateTemplate($input: TemplateInput!) {
      createTemplate(input: $input) { id name }
    }
    """
    variables = {"input": {"projectId": 1, "name": "tpl_live_test", "repoUrl": "repo", "tags": "test"}}
    resp = gql(mutation, variables)
    assert resp.status_code == 200
    t.join(timeout=5)
    assert any("tpl_live_test" in m for m in results)

# Аналогично можно реализовать тесты для on_doc_update, on_rule_update, on_template_update 