import requests
import time
import os
import asyncio
import websockets

MCP_URL = "http://localhost:8001"
API_KEY = os.getenv("MCP_API_KEY", "test")
PROJECT_ID = 1


def log_action(message):
    print(f"[AI-ASSISTANT] {message}")
    log_to_audit_and_changelog(message)


def log_to_audit_and_changelog(message):
    now = time.strftime("%Y-%m-%d %H:%M")
    with open("memory-bank/auditLog.md", "a", encoding="utf-8") as f:
        f.write(f"[{now}] [ai-assistant] [ACTION] {message}\n")
    with open("CHANGELOG.md", "a", encoding="utf-8") as f:
        f.write(f"[{now.split(' ')[0]}] ai: {message}\n")


def create_snapshot():
    resp = requests.post(
        f"{MCP_URL}/projects/{PROJECT_ID}/snapshot",
        headers={"X-API-KEY": API_KEY}
    )
    if resp.status_code == 200:
        archive = resp.json().get("archive")
        log_action(f"Снапшот создан: {archive}")
        return archive
    else:
        log_action(f"Ошибка создания снапшота: {resp.text}")


def rollback_to_snapshot(snapshot_name):
    resp = requests.post(
        f"{MCP_URL}/projects/{PROJECT_ID}/rollback",
        headers={"X-API-KEY": API_KEY},
        json={"snapshot": snapshot_name}
    )
    if resp.status_code == 200:
        log_action(f"Откат к снапшоту: {snapshot_name}")
    else:
        log_action(f"Ошибка отката: {resp.text}")


def create_knowledge_package(title, content):
    path = f"memory-bank/knowledge_packages/{title}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    log_action(f"Knowledge package создан: {path}")


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
        log_action("Обнаружены ошибки в auditLog.md:")
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
                # Реакция на merge/release/epic_done
                if any(event in msg for event in ["merge", "release", "epic_done"]):
                    log_action("Автоматически создаю снапшот по событию из WebSocket...")
                    create_snapshot()
    except Exception as e:
        log_action(f"Ошибка WebSocket: {e}")


def main_loop():
    # Запуск анализа auditLog.md
    analyze_audit_log()
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
    # Для асинхронного запуска WebSocket слушателя раскомментируйте:
    # import threading
    # threading.Thread(target=lambda: asyncio.run(listen_ws()), daemon=True).start()
    main_loop() 