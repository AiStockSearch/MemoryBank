import requests
import time
import os

MCP_URL = "http://localhost:8001"
API_KEY = os.getenv("MCP_API_KEY", "test")
PROJECT_ID = 1


def log_action(message):
    print(f"[AI-ASSISTANT] {message}")


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


def prompt_user(prompt):
    answer = input(f"{prompt} (y/n): ")
    return answer.strip().lower() == "y"


def main_loop():
    while True:
        # Пример: раз в неделю предлагать сделать снапшот
        if prompt_user("Рекомендую создать снапшот перед merge — создать сейчас?"):
            create_snapshot()
        # Пример: обнаружен баг
        if prompt_user("Обнаружен баг — создать knowledge package и зафиксировать?"):
            create_knowledge_package(
                "bug-example",
                "# Knowledge Package: bug-example\n\n## Описание\nОписание бага...\n"
            )
        # Пример: откат к снапшоту
        if prompt_user("В последних коммитах много ошибок. Откатить к снапшоту snapshot-X?"):
            rollback_to_snapshot("snapshot-X")
        # Пример: завершить итерацию
        if prompt_user("Завершить работу AI-ассистента?"):
            break
        time.sleep(10)  # Пауза между итерациями


if __name__ == "__main__":
    main_loop() 