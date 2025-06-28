from fastapi import FastAPI, HTTPException, Depends, Request, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from cacd import CACD
from typing import Optional
import json
from fastapi.responses import HTMLResponse, StreamingResponse
import logging
import os
import pync
import io
import zipfile

app = FastAPI()
dsn = os.getenv("DB_DSN")
cacd = CACD(dsn)

API_KEY = "supersecretkey"  # Можно вынести в переменные окружения

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Хранилище подключённых WebSocket-клиентов
ws_clients = set()

def verify_api_key(request: Request):
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

class TaskRequest(BaseModel):
    command: str
    task_id: str

class RuleRequest(BaseModel):
    rules: list

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    origin: str

DEFAULT_RULES = [
    {"id": "rule_default_priority", "type": "priority", "value": "medium", "description": "Default priority for new projects"}
]
DEFAULT_TEMPLATES = [
    {"name": "Base README", "repo_url": "https://github.com/example/base-readme", "tags": ["readme", "docs"]}
]

@app.post('/tasks', dependencies=[Depends(verify_api_key)])
async def create_task(req: TaskRequest):
    logger.info(f"Создание задачи: {req.task_id}")
    task = await cacd.process_command(req.command, req.task_id)
    msg = f"Создана задача {task['id']} для проекта {task.get('project_id', '')}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "created", "task": task}

@app.get('/context/{task_id}', dependencies=[Depends(verify_api_key)])
async def get_context(task_id: str):
    logger.info(f"Получение контекста для задачи: {task_id}")
    context = await cacd.memory.get_context(task_id)
    if context is None:
        logger.warning(f"Контекст не найден: {task_id}")
        raise HTTPException(status_code=404, detail="Context not found")
    return {"task_id": task_id, "context": context}

@app.post('/rules', dependencies=[Depends(verify_api_key)])
async def update_rules(req: RuleRequest):
    logger.info("Обновление правил")
    with open(cacd.rules_path, 'w') as f:
        json.dump(req.rules, f, indent=2)
    cacd._load_rules()
    msg = "Обновлены правила проекта"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "rules updated"}

@app.get('/rules', dependencies=[Depends(verify_api_key)])
async def get_rules():
    with open(cacd.rules_path, 'r') as f:
        rules = json.load(f)
    return rules

@app.get('/readme', response_class=HTMLResponse)
def get_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        # Преобразуем Markdown в HTML (простой способ)
        import markdown
        html = markdown.markdown(content)
        return f"<html><body>{html}</body></html>"
    except Exception as e:
        return HTMLResponse(f"<pre>README.md not found or error: {e}</pre>", status_code=404)

@app.post('/projects')
async def create_project(req: ProjectCreateRequest):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'INSERT INTO projects (name, description, origin) VALUES ($1, $2, $3) RETURNING id',
            req.name, req.description, req.origin
        )
        project_id = row["id"]
        # Инициализация дефолтных правил
        for rule in DEFAULT_RULES:
            await conn.execute(
                'INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)',
                rule["id"], project_id, rule["type"], rule["value"], rule["description"]
            )
        # Инициализация дефолтных шаблонов
        for tpl in DEFAULT_TEMPLATES:
            await conn.execute(
                'INSERT INTO templates (project_id, name, repo_url, tags) VALUES ($1, $2, $3, $4)',
                project_id, tpl["name"], tpl["repo_url"], tpl["tags"]
            )
        return {"project_id": project_id}

@app.get('/projects/by_origin')
async def get_project_by_origin(origin: str = Query(...)):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT id FROM projects WHERE origin = $1', origin)
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"project_id": row["id"]}

@app.websocket('/ws/notify')
async def websocket_notify(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # ping/pong или просто держим соединение
    except WebSocketDisconnect:
        ws_clients.remove(websocket)

# Функция для отправки уведомления всем WebSocket-клиентам
async def notify_ws_clients(message: str):
    for ws in list(ws_clients):
        try:
            await ws.send_text(message)
        except Exception:
            ws_clients.discard(ws)

# Функция для отправки push-уведомления на Mac
def notify_mac(title: str, message: str):
    try:
        pync.notify(message, title=title)
    except Exception as e:
        print(f"Push notification error: {e}")

# Пример использования уведомлений (можно вызывать из endpoint'ов)
# await notify_ws_clients("Новая задача создана!")
# notify_mac("MCP", "Новая задача создана!")

@app.post('/docs', dependencies=[Depends(verify_api_key)])
async def create_doc(project_id: int, type: str, content: str):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO docs (project_id, type, content) VALUES ($1, $2, $3)',
            project_id, type, content
        )
    msg = f"Добавлен документ типа {type} для проекта {project_id}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "doc created"}

@app.get('/projects/{project_id}/export', dependencies=[Depends(verify_api_key)])
async def export_project(project_id: int):
    """
    Экспортирует проект и все связанные сущности в zip-архив.
    """
    # Получаем все данные
    tasks = await cacd.memory.get_all_tasks(project_id)
    rules = await cacd.memory.get_all_rules(project_id)
    templates = await cacd.memory.get_all_templates(project_id)
    embeddings = await cacd.memory.get_all_embeddings(project_id)
    docs = await cacd.memory.get_all_docs(project_id)
    history = await cacd.memory.get_all_history(project_id)

    # Формируем zip-архив в памяти
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('tasks.json', json.dumps(tasks, ensure_ascii=False, indent=2))
        zipf.writestr('rules.json', json.dumps(rules, ensure_ascii=False, indent=2))
        zipf.writestr('templates.json', json.dumps(templates, ensure_ascii=False, indent=2))
        zipf.writestr('embeddings.json', json.dumps(embeddings, ensure_ascii=False, indent=2))
        zipf.writestr('docs.json', json.dumps(docs, ensure_ascii=False, indent=2))
        zipf.writestr('history.json', json.dumps(history, ensure_ascii=False, indent=2))
    zip_buffer.seek(0)

    # Логируем экспорт в changelog (history)
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO history (project_id, action, details) VALUES ($1, $2, $3)',
            project_id, 'export', json.dumps({'files': ['tasks.json', 'rules.json', 'templates.json', 'embeddings.json', 'docs.json', 'history.json']})
        )

    # Push-уведомление
    msg = f"Проект {project_id} экспортирован в архив"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)

    return StreamingResponse(zip_buffer, media_type='application/zip', headers={
        'Content-Disposition': f'attachment; filename="project_{project_id}_export.zip"'
    }) 