import requests
import sys
import asyncio
import websockets
import pytest

BASE = "http://127.0.0.1:8010"
ORIGIN = "cursor"


def check_rest():
    try:
        print("Проверка /projects/{origin}/export ...")
        r = requests.get(f"{BASE}/projects/{ORIGIN}/export")
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/backlog ...")
        r = requests.get(f"{BASE}/projects/{ORIGIN}/backlog")
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/tasks (POST) ...")
        r = requests.post(f"{BASE}/projects/{ORIGIN}/tasks", json={"command": "test", "task_id": "test-001"})
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/context/test-001 ...")
        r = requests.get(f"{BASE}/projects/{ORIGIN}/context/test-001")
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/knowledge/test-package ...")
        r = requests.get(f"{BASE}/projects/{ORIGIN}/knowledge/test-package")
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/feedback ...")
        r = requests.get(f"{BASE}/projects/{ORIGIN}/feedback")
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

        print("Проверка /projects/{origin}/report (POST) ...")
        r = requests.post(f"{BASE}/projects/{ORIGIN}/report", json={"context": {"task_id": "test-001", "summary": "test"}})
        print("OK" if r.status_code == 200 else f"FAIL: {r.text}")

    except Exception as e:
        print("REST error:", e)
        sys.exit(1)

async def check_ws():
    try:
        print("Проверка WebSocket ...")
        uri = f"ws://127.0.0.1:8010/ws/events"
        async with websockets.connect(uri) as ws:
            await ws.send("ping")
            msg = await ws.recv()
            print("OK" if "Echo" in msg else f"FAIL: {msg}")
    except Exception as e:
        print("WebSocket error:", e)
        sys.exit(1)

def test_export():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/export")
    assert r.status_code == 200
    assert "archive/cursor/export_cursor.zip" in r.text

def test_backlog_not_found():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/backlog")
    assert r.status_code == 404
    assert "backlog not found" in r.text

def test_feedback():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/feedback")
    assert r.status_code == 200
    assert "test feedback" in r.text

def test_knowledge_package():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/knowledge/test-package")
    assert r.status_code == 200
    assert "test knowledge" in r.text

def test_context():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/context/test-001")
    assert r.status_code == 200
    assert "test-001" in r.text

def test_create_task():
    r = requests.post(f"{BASE}/projects/{ORIGIN}/tasks", json={"command": "test", "task_id": "test-001"})
    assert r.status_code == 200
    assert "created" in r.text

def test_report():
    r = requests.post(f"{BASE}/projects/{ORIGIN}/report", json={"context": {"task_id": "test-001", "summary": "test"}})
    assert r.status_code == 200
    assert "Отчёт по задаче test-001" in r.text

def test_invalid_endpoint():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/invalid")
    assert r.status_code == 404

def test_invalid_method():
    r = requests.get(f"{BASE}/projects/{ORIGIN}/tasks")
    assert r.status_code in (405, 404)

def test_invalid_data():
    r = requests.post(f"{BASE}/projects/{ORIGIN}/tasks", json={"cmd": "bad"})
    assert r.status_code == 422

@pytest.mark.asyncio
async def test_websocket_echo():
    uri = "ws://127.0.0.1:8010/ws/events"
    async with websockets.connect(uri) as ws:
        await ws.send("ping")
        msg = await ws.recv()
        assert "Echo" in msg

@pytest.mark.asyncio
async def test_websocket_invalid():
    uri = "ws://127.0.0.1:8010/ws/events"
    async with websockets.connect(uri) as ws:
        with pytest.raises(TypeError):
            await ws.send(1234)

@pytest.mark.asyncio
async def test_websocket_disconnect():
    uri = "ws://127.0.0.1:8010/ws/events"
    ws = await websockets.connect(uri)
    await ws.send("disconnect")
    await ws.close()
    assert ws.close_code is not None

if __name__ == "__main__":
    check_rest()
    asyncio.run(check_ws())
    print("Все проверки завершены.") 