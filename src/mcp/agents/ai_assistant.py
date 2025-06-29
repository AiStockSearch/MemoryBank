import requests
import time
import os
import asyncio
import websockets
import json
from src.mcp.tools.ai_utils import log_action, generate_task_summary, analyze_task_links, generate_mermaid_diagram

MCP_URL = "http://localhost:8001"
API_KEY = os.getenv("API_KEY", "supersecretkey")
PROJECT_ID = 1


def get_tasks():
    # Пример: получить задачи из tasks.mdf (или через MCP API)
    path = "memory-bank/tasks/business-tasks.md"
    if not os.path.exists(path):
        return []
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("| ") and "|" in line[2:]:
                parts = [x.strip() for x in line.strip().split("|") if x.strip()]
                if len(parts) >= 5:
                    tasks.append({
                        "id": parts[0],
                        "title": parts[1],
                        "status": parts[2],
                        "epic": parts[3],
                        "business_goal": parts[4],
                        "description": ""
                    })
    return tasks


def create_snapshot():
    try:
        resp = requests.post(
            f"{MCP_URL}/projects/{PROJECT_ID}/snapshot",
            headers={"X-API-KEY": API_KEY}
        )
        if resp.status_code == 200:
            archive = resp.json().get("archive")
            log_action(f"Снапшот создан: {archive}")
            return archive
        else:
            log_action(f"Ошибка создания снапшота: {resp.text}", level="ERROR")
    except Exception as e:
        log_action(f"Ошибка создания снапшота: {e}", level="ERROR")


def rollback_to_snapshot(snapshot_name):
    try:
        resp = requests.post(
            f"{MCP_URL}/projects/{PROJECT_ID}/rollback",
            headers={"X-API-KEY": API_KEY},
            json={"snapshot": snapshot_name}
        )
        if resp.status_code == 200:
            log_action(f"Откат к снапшоту: {snapshot_name}")
        else:
            log_action(f"Ошибка отката: {resp.text}", level="ERROR")
    except Exception as e:
        log_action(f"Ошибка отката: {e}", level="ERROR")


def create_knowledge_package(title, content):
    path = f"memory-bank/knowledge_packages/{title}.md"
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        log_action(f"Knowledge package создан: {path}")
    except Exception as e:
        log_action(f"Ошибка создания knowledge package: {e}", level="ERROR")


def generate_kp_template(event_type, details=""):
    if event_type == "bug":
        return f"# Knowledge Package: bug-{details}\n\n## Описание\nОписание бага: {details}\n"
    elif event_type == "feature":
        return f"# Knowledge Package: feature-{details}\n\n## Описание\nОписание фичи: {details}\n"
    elif event_type == "epic":
        return f"# Knowledge Package: epic-{details}\n\n## Описание\nEpic: {details}\n"
    else:
        return f"# Knowledge Package: {details}\n\n## Описание\nАвтоматически сгенерировано.\n"


def analyze_audit_log():
    path = "memory-bank/auditLog.md"
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-10:]
    errors = [line for line in lines if "ERROR" in line or "ошибка" in line.lower()]
    if errors:
        log_action("Обнаружены ошибки в auditLog.md:", level="WARNING")
        for err in errors:
            print(err.strip())
        if prompt_user("Обнаружены ошибки. Откатить к последнему снапшоту?"):
            rollback_to_snapshot("snapshot-X")


def prompt_user(prompt):
    answer = input(f"{prompt} (y/n): ")
    return answer.strip().lower() == "y"


async def listen_ws():
    uri = "ws://localhost:8001/ws/notify"
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                msg = await websocket.recv()
                log_action(f"WS notification: {msg}")
                if any(event in msg for event in ["merge", "release", "epic_done"]):
                    log_action("Автоматически создаю снапшот по событию из WebSocket...")
                    create_snapshot()
    except Exception as e:
        log_action(f"Ошибка WebSocket: {e}", level="ERROR")


def main_loop():
    analyze_audit_log()
    tasks = get_tasks()
    # Генерация summary по задачам
    for task in tasks:
        summary = generate_task_summary(task)
        out_path = f"memory-bank/knowledge_packages/summary-task-{task['id']}.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(summary)
        log_action(f"Summary по задаче {task['id']} сгенерирован и сохранён в {out_path}")
    # Анализ связей между задачами и бизнес-целями
    missing_links = analyze_task_links(tasks)
    if missing_links:
        log_action(f"Задачи без связей с epic/business_goal: {missing_links}", level="WARNING")
        # Генерация визуализации связей
    generate_mermaid_diagram("task_links", [(t['id'], t.get('epic','-'), t.get('business_goal','-')) for t in tasks], "memory-bank/knowledge_packages/task_links.mmd")
    # Можно добавить запуск listen_ws в отдельном потоке/таске
    # asyncio.run(listen_ws())
    while True:
        if prompt_user("Рекомендую создать снапшот перед merge — создать сейчас?"):
            create_snapshot()
        if prompt_user("Обнаружен баг — создать knowledge package и зафиксировать?"):
            kp_content = generate_kp_template("bug", "example-bug")
            create_knowledge_package("bug-example", kp_content)
        if prompt_user("В последних коммитах много ошибок. Откатить к снапшоту snapshot-X?"):
            rollback_to_snapshot("snapshot-X")
        if prompt_user("Завершить работу AI-ассистента?"):
            break
        time.sleep(10)


if __name__ == "__main__":
    main_loop() 