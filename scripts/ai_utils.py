import os
import time
import json

def log_action(message, level="INFO"):
    now = time.strftime("%Y-%m-%d %H:%M")
    log_line = f"[{now}] [{level}] [ai-assistant] {message}\n"
    with open("memory-bank/auditLog.md", "a", encoding="utf-8") as f:
        f.write(log_line)
    with open("CHANGELOG.md", "a", encoding="utf-8") as f:
        f.write(f"[{now.split(' ')[0]}] ai: {message}\n")
    print(f"[AI-ASSISTANT][{level}] {message}")

def generate_mermaid_diagram(diagram_type, data, out_path):
    if diagram_type == "task_lifecycle":
        mermaid = '''flowchart TD\n    BZ[Бизнесовая задача] -->|Декомпозиция| PLAN[Планирование]\n    PLAN -->|Если нужен креатив| CREATIVE[Креатив]\n    CREATIVE --> PLAN\n    PLAN -->|Готово к реализации| IMPLEMENT[Реализация]\n    IMPLEMENT --> REFLECT[Ретроспектива/Архив]\n    REFLECT -->|Новые инсайты| PLAN\n    PLAN -->|Если не нужен креатив| IMPLEMENT\n    BZ -->|Иногда напрямую| PLAN\n'''
    elif diagram_type == "task_links":
        # data: list of (task, epic, business_goal)
        nodes = set()
        edges = []
        for t, e, b in data:
            nodes.update([t, e, b])
            edges.append(f'    {t} --> {e}')
            edges.append(f'    {e} --> {b}')
        mermaid = 'flowchart TD\n' + '\n'.join(edges)
    elif diagram_type == "roadmap":
        # data: list of (этап, дата_начала, дата_конца, статус)
        mermaid = 'gantt\n    title Roadmap\n    dateFormat  YYYY-MM-DD\n'
        for stage, start, end, status in data:
            mermaid += f'    section {stage}\n    {stage} :{status}, {stage}, {start},{end}\n'
    else:
        mermaid = "flowchart TD\n    A[Start] --> B[End]"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"```mermaid\n{mermaid}\n```")
    log_action(f"Mermaid-диаграмма {diagram_type} сохранена в {out_path}")

def generate_task_summary(task):
    # task: dict с ключами id, title, status, epic, business_goal, description
    summary = f"# Summary for Task {task['id']}\n"
    summary += f"**Title:** {task.get('title','')}\n\n"
    summary += f"**Status:** {task.get('status','')}\n\n"
    summary += f"**Epic:** {task.get('epic','-')}\n\n"
    summary += f"**Business Goal:** {task.get('business_goal','-')}\n\n"
    summary += f"**Description:** {task.get('description','')}\n\n"
    summary += f"**AI-summary:** (здесь будет автоматически сгенерированное резюме)\n"
    return summary

def analyze_task_links(tasks):
    # tasks: list of dicts с ключами id, epic, business_goal
    missing_links = []
    for t in tasks:
        if not t.get('epic') or not t.get('business_goal'):
            missing_links.append(t['id'])
    return missing_links

def review_changelog(changelog_path="CHANGELOG.md"):
    if not os.path.exists(changelog_path):
        print("CHANGELOG.md не найден")
        return
    with open(changelog_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    errors = [l for l in lines if any(w in l.lower() for w in ["error", "ошибка", "fail", "bug", "critical"])]
    summary = f"Всего изменений: {len(lines)}\n"
    summary += f"Найдено ошибок/аномалий: {len(errors)}\n"
    if errors:
        summary += "\nПоследние ошибки/аномалии:\n" + ''.join(errors[-5:])
    else:
        summary += "\nОшибок и аномалий не найдено.\n"
    recommendations = ""
    if len(errors) > 0:
        recommendations += "Рекомендуется провести аудит последних изменений, проверить тесты и рассмотреть откат к стабильному снапшоту.\n"
    if len(lines) > 50:
        recommendations += "Рекомендуется архивировать старые записи changelog для ускорения анализа.\n"
    return summary, recommendations

def generate_roadmap(tasks):
    # tasks: list of dicts с ключами id, title, status, epic, business_goal, start, end
    # Группируем по epic или статусу, строим Gantt-диаграмму
    stages = []
    for t in tasks:
        stage = t.get('epic') or t.get('title')
        start = t.get('start', '2024-06-01')
        end = t.get('end', '2024-06-30')
        status = 'done' if t.get('status','').lower() in ['done','completed'] else 'active'
        stages.append((stage, start, end, status))
    return stages 