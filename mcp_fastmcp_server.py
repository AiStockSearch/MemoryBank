from fastmcp import FastMCP
from pathlib import Path
import shutil
import zipfile
import os

mcp = FastMCP('Cursor MCP Server')

@mcp.tool
def export_project(origin: str) -> str:
    """Экспортирует архив знаний origin в zip-файл и возвращает путь."""
    archive_dir = Path('archive') / origin
    if not archive_dir.exists():
        return f'Origin {origin} не найден.'
    out_path = archive_dir / f'export_{origin}.zip'
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(archive_dir):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(archive_dir.parent)
                zipf.write(full_path, rel_path)
    return str(out_path)

@mcp.resource
def get_backlog(origin: str) -> dict:
    """Возвращает backlog для origin."""
    backlog_path = Path('archive') / origin / 'federation_backlog.md'
    if not backlog_path.exists():
        return {'error': 'backlog not found'}
    return {'backlog': backlog_path.read_text(encoding='utf-8')}

@mcp.tool
def create_task(command: str, task_id: str) -> dict:
    """Создаёт задачу с заданным командой и id."""
    # TODO: интеграция с CACD/task engine
    return {"status": "created", "task_id": task_id, "command": command}

@mcp.resource
def get_context(task_id: str) -> dict:
    """Возвращает контекст задачи по task_id."""
    # TODO: интеграция с memory/context storage
    return {"task_id": task_id, "context": "..."}

@mcp.tool
def update_rules(rules: list, user_id: str) -> dict:
    """Обновляет правила для пользователя."""
    # TODO: интеграция с rules storage
    return {"status": "rules updated", "count": len(rules)}

@mcp.tool
def federation_pull_knowledge(origin: str, file: str) -> str:
    """Получает файл знаний из federation origin."""
    file_path = Path('archive') / origin / 'knowledge_packages' / file
    if not file_path.exists():
        return 'Файл не найден'
    return file_path.read_text(encoding='utf-8')

@mcp.resource
def get_knowledge_package(origin: str, name: str) -> dict:
    """Возвращает содержимое knowledge package."""
    kp_path = Path('archive') / origin / 'knowledge_packages' / name
    if not kp_path.exists():
        return {'error': 'not found'}
    return {'content': kp_path.read_text(encoding='utf-8')}

@mcp.resource
def get_feedback(origin: str) -> dict:
    """Возвращает feedback для origin."""
    fb_path = Path('archive') / origin / 'feedback.md'
    if not fb_path.exists():
        return {'error': 'not found'}
    return {'feedback': fb_path.read_text(encoding='utf-8')}

@mcp.prompt
def generate_report(context: dict) -> str:
    """Генерирует отчёт по задаче на основе контекста."""
    return f"Отчёт по задаче {context.get('task_id', '')}: {context.get('summary', 'нет данных')}"

if __name__ == '__main__':
    mcp.run() 