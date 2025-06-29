import requests
import sys
import asyncio
import websockets

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

if __name__ == "__main__":
    check_rest()
    asyncio.run(check_ws())
    print("Все проверки завершены.") 