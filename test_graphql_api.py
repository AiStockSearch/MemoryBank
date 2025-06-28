import pytest
from fastapi.testclient import TestClient
from mcp_server import app
import json

client = TestClient(app)

GRAPHQL_URL = "/graphql"

# Helper for GraphQL requests
def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = client.post(GRAPHQL_URL, json=payload)
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