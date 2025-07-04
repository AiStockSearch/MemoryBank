from fastapi import FastAPI, HTTPException, Depends, Request, Query, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Header, Body, status
from pydantic import BaseModel
from src.mcp.core.core import get_cacd
from src.mcp.memory.memory_bank import get_memory_bank
from typing import Optional, List, Any
import json
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse, PlainTextResponse
import logging
import os
import pync
import io
import zipfile
import tempfile
import shutil
import datetime
import subprocess
import glob
import hashlib
import boto3
import numpy as np
from sklearn.cluster import KMeans
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
import asyncio
from passlib.context import CryptContext
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from cursor_rules.fs_rules import list_rules, create_rule, update_rule, delete_rule, export_rules_zip, import_rules_zip, get_rule_changelog, rollback_rule
from cursor_rules.mdc_parser import validate_mdc
import base64
import httpx
import sys
import importlib.util
import yaml
import filecmp
from src.server.schemas.graphql_schema import schema

# Импортируем генератор memory-bank
from src.mcp.memory.generate_memory_bank import generate_memory_bank, TEMPLATES

# Импортируем и монтируем все endpoint'ы из fastmcp_api.py
from src.server.api.fastmcp_api import app as fastmcp_app

app = FastAPI()
app.mount("/api", fastmcp_app)

API_KEY = os.getenv("API_KEY", "supersecretkey")
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretjwtkey")

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Хранилище подключённых WebSocket-клиентов
ws_clients = set()

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

WHITELIST_PATHS = {'/auth/login', '/auth/register'}

# In-memory хранилище webhook-URL (можно заменить на БД)
registered_webhooks = set()

def verify_api_key(request: Request):
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post('/webhooks/register', dependencies=[Depends(verify_api_key)])
async def register_webhook(url: str = Body(..., embed=True)):
    registered_webhooks.add(url)
    return {"status": "registered", "url": url}

@app.post('/webhooks/unregister', dependencies=[Depends(verify_api_key)])
async def unregister_webhook(url: str = Body(..., embed=True)):
    registered_webhooks.discard(url)
    return {"status": "unregistered", "url": url}

async def send_rule_webhook(event: str, path: str, meta: dict, user_id: str, reason: str = ""):
    payload = {
        "event": event,  # create/update/delete/import/rollback
        "path": path,
        "meta": meta,
        "user_id": user_id,
        "reason": reason
    }
    for url in list(registered_webhooks):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Webhook send error to {url}: {e}")

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пропуск для whitelist
        if request.url.path in WHITELIST_PATHS:
            return await call_next(request)
        # Пропуск для GraphQL queries
        if request.url.path == '/graphql':
            body = await request.body()
            if b'"query"' in body and b'mutation' not in body:
                return await call_next(request)
        # Проверка JWT
        auth_header = request.headers.get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JSONResponse(status_code=403, content={"detail": "Требуется авторизация"})
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get('role')
            user_id = payload.get('sub')
            if role not in ('root', 'agent'):
                return JSONResponse(status_code=403, content={"detail": "Недостаточно прав"})
            request.state.user_id = user_id
            request.state.role = role
        except JWTError:
            return JSONResponse(status_code=403, content={"detail": "Неверный или просроченный токен"})
        return await call_next(request)

app.add_middleware(JWTAuthMiddleware)

class TaskRequest(BaseModel):
    command: str
    task_id: str

class RuleRequest(BaseModel):
    rules: list

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    origin: str

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

DEFAULT_RULES = [
    {"id": "rule_default_priority", "type": "priority", "value": "medium", "description": "Default priority for new projects"}
]
DEFAULT_TEMPLATES = [
    {"name": "Base README", "repo_url": "https://github.com/example/base-readme", "tags": ["readme", "docs"]}
]

@app.post('/tasks', dependencies=[Depends(verify_api_key)])
async def create_task(req: TaskRequest, memory_bank=Depends(get_memory_bank)):
    cacd = get_cacd(memory_bank)
    logger.info(f"Создание задачи: {req.task_id}")
    task = await cacd.process_command(req.command, req.task_id)
    msg = f"Создана задача {task['id']} для проекта {task.get('project_id', '')}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "created", "task": task}

@app.get('/context/{task_id}', dependencies=[Depends(verify_api_key)])
async def get_context(task_id: str, memory_bank=Depends(get_memory_bank)):
    logger.info(f"Получение контекста для задачи: {task_id}")
    context = await memory_bank.get_context(task_id)
    if context is None:
        logger.warning(f"Контекст не найден: {task_id}")
        raise HTTPException(status_code=404, detail="Context not found")
    return {"task_id": task_id, "context": context}

@app.post('/rules', dependencies=[Depends(verify_api_key)])
async def update_rules(req: RuleRequest, user_id: str = Header(None, alias="X-USER-ID")):
    logger.info("Обновление правил (MDC)")
    results = []
    for rule in req.rules:
        meta = rule.get('meta') or {}
        body = rule.get('body') or ''
        filename = rule.get('filename') if 'filename' in rule else None
        data = {'meta': meta, 'body': body}
        errors = validate_mdc(data)
        if errors:
            raise HTTPException(status_code=400, detail={"rule": meta.get('description'), "errors": errors})
        reason = rule.get('reason', 'bulk update')
        # Callback для webhooks
        def cb(event, path, meta, user_id, reason):
            asyncio.create_task(send_rule_webhook(event, path, meta, user_id, reason))
        # Если есть путь, обновляем, иначе создаём
        if 'path' in rule and rule['path']:
            update_rule(rule['path'], meta, body, user_id=user_id, reason=reason, on_change=cb)
            results.append({'status': 'updated', 'path': rule['path']})
        else:
            path = create_rule(meta, body, filename=filename, user_id=user_id, reason=reason, on_change=cb)
            results.append({'status': 'created', 'path': path})
    msg = "Обновлены правила (MDC)"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "rules updated", "results": results}

@app.get('/rules', dependencies=[Depends(verify_api_key)])
async def get_rules():
    return list_rules()

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
async def create_project(req: ProjectCreateRequest, memory_bank=Depends(get_memory_bank)):
    pool = await memory_bank.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'INSERT INTO projects (name, description, origin) VALUES ($1, $2, $3) RETURNING id',
            req.name, req.description, req.origin
        )
        project_id = row["id"]
        # Копируем глобальные правила
        global_rules = await conn.fetch('SELECT * FROM cursor_rules WHERE project_id IS NULL')
        for rule in global_rules:
            await conn.execute(
                'INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)',
                rule["id"] + f"_{project_id}", project_id, rule["type"], rule["value"], rule["description"]
            )
        # Копируем глобальные шаблоны
        global_templates = await conn.fetch('SELECT * FROM templates WHERE project_id IS NULL')
        for tpl in global_templates:
            await conn.execute(
                'INSERT INTO templates (project_id, name, repo_url, tags) VALUES ($1, $2, $3, $4)',
                project_id, tpl["name"], tpl["repo_url"], tpl["tags"]
            )
        return {"project_id": project_id}

@app.get('/projects/by_origin')
async def get_project_by_origin(origin: str = Query(...), memory_bank=Depends(get_memory_bank)):
    pool = await memory_bank.get_pool()
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
async def create_doc(project_id: int, type: str, content: str, user_id: str = Header(None, alias="X-USER-ID"), memory_bank=Depends(get_memory_bank)):
    pool = await memory_bank.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'INSERT INTO docs (project_id, type, content) VALUES ($1, $2, $3) RETURNING id',
            project_id, type, content
        )
        doc_id = row['id']
    msg = f"Добавлен документ типа {type} для проекта {project_id}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    # --- Автосохранение версии ---
    async with pool.acquire() as conn:
        vrow = await conn.fetchrow('SELECT max(version) as v FROM doc_versions WHERE doc_id = $1', doc_id)
        version = (vrow['v'] or 0) + 1
        await conn.execute('''INSERT INTO doc_versions (doc_id, project_id, version, data, user_id) VALUES ($1, $2, $3, $4, $5)''',
            doc_id, project_id, version, json.dumps({"type": type, "content": content}), user_id)
    return {"status": "doc created", "doc_id": doc_id}

@app.get('/docs/{doc_id}/versions')
async def get_doc_versions(doc_id: int, memory_bank=Depends(get_memory_bank)):
    pool = await memory_bank.get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT version, data, user_id, created_at FROM doc_versions WHERE doc_id = $1 ORDER BY version DESC', doc_id)
        return [{"version": r["version"], "user_id": r["user_id"], "created_at": r["created_at"], "data": r["data"]} for r in rows]

@app.post('/docs/{doc_id}/rollback')
async def rollback_doc(doc_id: int, version: int, user_id: str = Header(None, alias="X-USER-ID"), memory_bank=Depends(get_memory_bank)):
    pool = await memory_bank.get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT data, project_id FROM doc_versions WHERE doc_id = $1 AND version = $2', doc_id, version)
        if not row:
            raise HTTPException(status_code=404, detail="Версия не найдена")
        data = json.loads(row['data'])
        project_id = row['project_id']
        # Перезаписываем документ
        await conn.execute('''UPDATE docs SET type=$1, content=$2 WHERE id=$3''',
            data.get('type'), data.get('content'), doc_id)
        # Сохраняем новую версию (rollback)
        vrow = await conn.fetchrow('SELECT max(version) as v FROM doc_versions WHERE doc_id = $1', doc_id)
        new_version = (vrow['v'] or 0) + 1
        await conn.execute('''INSERT INTO doc_versions (doc_id, project_id, version, data, user_id) VALUES ($1, $2, $3, $4, $5)''',
            doc_id, project_id, new_version, json.dumps(data), user_id)
    return {"status": "rolled_back", "doc_id": doc_id, "version": version}

@app.get('/projects/{project_id}/export', dependencies=[Depends(verify_api_key)])
async def export_project(project_id: int, user_id: str = Header(None, alias="X-USER-ID"), memory_bank=Depends(get_memory_bank)):
    """
    Экспортирует проект и все связанные сущности в zip-архив в archive/<origin>/.
    """
    # Получаем все данные
    tasks = await memory_bank.get_all_tasks(project_id)
    rules = await memory_bank.get_all_rules(project_id)
    templates = await memory_bank.get_all_templates(project_id)
    embeddings = await memory_bank.get_all_embeddings(project_id)
    docs = await memory_bank.get_all_docs(project_id)
    history = await memory_bank.get_all_history(project_id)

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

    # Сохраняем архив в archive/<origin>/
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    archive_dir = os.path.join('archive', str(project_id))
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f'export_{now}.zip')
    with open(archive_path, 'wb') as f:
        f.write(zip_buffer.getvalue())

    # Логируем экспорт в changelog (history)
    pool = await memory_bank.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)',
            project_id, user_id, 'export', json.dumps({'archive_path': archive_path})
        )

    msg = f"Проект {project_id} экспортирован в архив {archive_path}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)

    return {
        "status": "exported",
        "archive_path": archive_path,
        "download_url": f"/download/{archive_path}"
    }

@app.post('/projects/{project_id}/merge', dependencies=[Depends(verify_api_key)])
async def merge_project(
    project_id: int,
    archive_path: str = Body(...),  # путь к архиву в archive/<origin>/
    dry_run: bool = Form(False),
    user_id: str = Header(None, alias="X-USER-ID")
):
    """
    Импортирует архив только из archive/<origin>/, валидация по origin, логирование.
    """
    import zipfile, os, tempfile, shutil, filecmp
    expected_dir = os.path.join('archive', str(project_id))
    if not archive_path.startswith(expected_dir):
        raise HTTPException(status_code=400, detail="Archive must be in archive/<origin>/")
    if not os.path.exists(archive_path):
        raise HTTPException(status_code=404, detail="Archive file not found")
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(tmpdir)
        # (Дальнейшая логика merge как раньше)
        # ...
    # Логирование merge
    msg = f"Merge архива {archive_path} в проект {project_id} завершён."
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    # ...
    return {"status": "merged", "archive_path": archive_path}

@app.post('/projects/{project_id}/release', dependencies=[Depends(verify_api_key)])
async def release_project(
    project_id: int,
    user_id: str = Header(None, alias="X-USER-ID")
):
    """
    Выпуск новой версии (release) проекта. После release автоматически создаёт снапшот.
    """
    # ... логика release ...
    import requests
    try:
        resp = requests.post(
            f'http://localhost:8001/projects/{project_id}/snapshot',
            headers={'X-USER-ID': user_id, 'X-API-KEY': os.getenv('API_KEY', 'test')}
        )
        snap = resp.json().get('archive')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        mb_path = os.path.join('memory-bank')
        audit_path = os.path.join(mb_path, 'auditLog.md')
        with open(audit_path, 'a', encoding='utf-8') as f:
            f.write(f"[{now}] [{user_id}] [SNAPSHOT] Снапшот {snap} создан после release\n")
        changelog_path = os.path.join('CHANGELOG.md')
        with open(changelog_path, 'a', encoding='utf-8') as f:
            f.write(f"[{now.split(' ')[0]}] snapshot: Снапшот {snap} создан после release\n")
    except Exception as e:
        print(f"Ошибка создания снапшота после release: {e}")
    # ... остальной код ...

@app.post('/epic/{epic_id}/complete', dependencies=[Depends(verify_api_key)])
async def complete_epic(
    epic_id: int,
    project_id: int = Body(...),
    user_id: str = Header(None, alias="X-USER-ID")
):
    """
    Завершение Epic. После завершения Epic автоматически создаёт снапшот.
    """
    # ... логика завершения Epic ...
    import requests
    try:
        resp = requests.post(
            f'http://localhost:8001/projects/{project_id}/snapshot',
            headers={'X-USER-ID': user_id, 'X-API-KEY': os.getenv('API_KEY', 'test')}
        )
        snap = resp.json().get('archive')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        mb_path = os.path.join('memory-bank')
        audit_path = os.path.join(mb_path, 'auditLog.md')
        with open(audit_path, 'a', encoding='utf-8') as f:
            f.write(f"[{now}] [{user_id}] [SNAPSHOT] Снапшот {snap} создан после завершения Epic {epic_id}\n")
        changelog_path = os.path.join('CHANGELOG.md')
        with open(changelog_path, 'a', encoding='utf-8') as f:
            f.write(f"[{now.split(' ')[0]}] snapshot: Снапшот {snap} создан после завершения Epic {epic_id}\n")
    except Exception as e:
        print(f"Ошибка создания снапшота после завершения Epic: {e}")
    # ... остальной код ...

def echo_action(params):
    return {"echo": params["msg"]}

def archive_knowledge_package_action(params):
    import shutil, os
    src = os.path.join('memory-bank', 'knowledge_packages', params['file'])
    dst = os.path.join('memory-bank', 'archive', params['file'])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    return {'archived': params['file']}

def search_knowledge_action(params):
    import os
    results = []
    for fname in os.listdir('memory-bank/knowledge_packages'):
        path = os.path.join('memory-bank/knowledge_packages', fname)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            if params['keyword'] in f.read():
                results.append(fname)
    return {'found': results}

def batch_update_status_action(params):
    import os
    updated = []
    for fname in params['files']:
        path = os.path.join('memory-bank/tasks', fname)
        if os.path.exists(path):
            with open(path, 'r+') as f:
                content = f.read()
                if 'Статус:' in content:
                    # Примитивная замена статуса
                    import re
                    content = re.sub(r'Статус:.*', f'Статус: {params["status"]}', content)
                else:
                    content += f'\nСтатус: {params["status"]}\n'
                f.seek(0)
                f.write(content)
                f.truncate()
            updated.append(fname)
    return {'updated': updated}

def generate_report_action(params):
    import os
    report = []
    for fname in os.listdir('memory-bank/knowledge_packages'):
        report.append(f'Knowledge: {fname}')
    return {'report': report}

def analyze_changelog_action(params):
    import os
    path = os.path.join('memory-bank', 'CHANGELOG.md')
    if not os.path.exists(path):
        return {'error': 'CHANGELOG.md not found'}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    summary = []
    anomalies = []
    for line in lines:
        if 'fix:' in line or 'error' in line.lower():
            anomalies.append(line.strip())
        if 'feat:' in line:
            summary.append(line.strip())
    return {'summary': summary, 'anomalies': anomalies}

def generate_best_practices_action(params):
    import os
    practices = []
    path = os.path.join('memory-bank', 'systemPatterns.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        in_section = False
        for line in lines:
            if 'Best practices' in line:
                in_section = True
            elif in_section and (line.strip() == '' or line.startswith('#')):
                in_section = False
            elif in_section:
                practices.append(line.strip())
    return {'best_practices': practices}

def ai_review_changes_action(params):
    import os
    path = os.path.join('memory-bank', 'CHANGELOG.md')
    if not os.path.exists(path):
        return {'error': 'CHANGELOG.md not found'}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()[-10:]
    improvements = []
    risks = []
    for line in lines:
        if 'refactor' in line or 'improve' in line:
            improvements.append(line.strip())
        if 'risk' in line or 'breaking' in line:
            risks.append(line.strip())
    return {'improvements': improvements, 'risks': risks}

CUSTOM_COMMAND_ACTIONS = {
    'echo_action': echo_action,
    'archive_knowledge_package_action': archive_knowledge_package_action,
    'search_knowledge_action': search_knowledge_action,
    'batch_update_status_action': batch_update_status_action,
    'generate_report_action': generate_report_action,
    'analyze_changelog_action': analyze_changelog_action,
    'generate_best_practices_action': generate_best_practices_action,
    'ai_review_changes_action': ai_review_changes_action,
    # Здесь можно регистрировать другие action-функции
}

@app.post('/custom_command/{command_name}')
async def run_custom_command(command_name: str, request: Request):
    params = await request.json()
    cmd_path = os.path.join('memory-bank', 'custom_commands', f'{command_name}.yaml')
    if not os.path.exists(cmd_path):
        raise HTTPException(status_code=404, detail=f'Custom command {command_name} not found')
    with open(cmd_path, 'r') as f:
        cmd = yaml.safe_load(f)
    action_name = cmd.get('action')
    result = None
    if action_name and action_name in CUSTOM_COMMAND_ACTIONS:
        result = CUSTOM_COMMAND_ACTIONS[action_name](params)
    return {
        'status': 'ok',
        'command': command_name,
        'description': cmd.get('description'),
        'parameters': params,
        'action': action_name,
        'result': result
    }

@app.post('/memory-bank/import')
async def import_memory_bank(file: UploadFile = File(...)):
    import zipfile, os
    with zipfile.ZipFile(file.file) as zf:
        zf.extractall('memory-bank/')
    return {"status": "imported"}

@app.get('/memory-bank/export')
async def export_memory_bank():
    import zipfile, io, os
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for root, dirs, files in os.walk('memory-bank/'):
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), 'memory-bank/'))
    mem_zip.seek(0)
    return StreamingResponse(mem_zip, media_type='application/zip', headers={'Content-Disposition': 'attachment; filename=memory-bank.zip'})

@app.post('/memory-bank/merge')
async def merge_memory_bank(
    archive: UploadFile = File(...),
    dry_run: bool = Form(True)
):
    import zipfile, os, io
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(archive.file) as zf:
            zf.extractall(tmpdir)
        diff = []
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), tmpdir)
                target_path = os.path.join('memory-bank', rel_path)
                if not os.path.exists(target_path):
                    diff.append(f'NEW: {rel_path}')
                elif not filecmp.cmp(os.path.join(root, f), target_path, shallow=False):
                    diff.append(f'CHANGED: {rel_path}')
        for root, dirs, files in os.walk('memory-bank'):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), 'memory-bank')
                if not os.path.exists(os.path.join(tmpdir, rel_path)):
                    diff.append(f'DELETED: {rel_path}')
        if dry_run:
            return {'status': 'dry-run', 'diff': diff}
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), tmpdir)
                target_path = os.path.join('memory-bank', rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(os.path.join(root, f), target_path)
        return {'status': 'merged', 'diff': diff}

@app.post('/memory-bank/rollback')
async def rollback_memory_bank(snapshot: UploadFile = File(...)):
    import zipfile, os, shutil, tempfile
    # Удаляем текущую memory-bank/
    if os.path.exists('memory-bank'):
        shutil.rmtree('memory-bank')
    # Распаковываем архив в memory-bank/
    with zipfile.ZipFile(snapshot.file) as zf:
        zf.extractall('memory-bank/')
        restored_files = zf.namelist()
    return {'status': 'rolled back', 'restored_files': restored_files}

@app.post('/memory-bank/batch')
async def batch_apply_memory_bank(batch: UploadFile = File(...)):
    import zipfile, os
    added = []
    with zipfile.ZipFile(batch.file) as zf:
        for member in zf.namelist():
            if member.endswith('/'):
                continue
            target_path = os.path.join('memory-bank', member)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'wb') as out_f:
                out_f.write(zf.read(member))
            added.append(member)
    return {'status': 'batch applied', 'files': added}

@app.get('/federation/{origin}/pull_knowledge')
async def federation_pull_knowledge(origin: str, file: str):
    path = os.path.join('archive', origin, 'knowledge_packages', file)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Knowledge package not found')
    # TODO: логировать операцию
    return FileResponse(path, filename=file)

@app.post('/federation/{origin}/push_knowledge')
async def federation_push_knowledge(origin: str, file: UploadFile = File(...)):
    import os
    path = os.path.join('archive', origin, 'knowledge_packages', file.filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as out_f:
        out_f.write(await file.read())
    # TODO: логировать операцию
    return {'status': 'uploaded', 'file': file.filename}

@app.get('/federation/{origin}/pull_command')
async def federation_pull_command(origin: str, file: str):
    import os
    path = os.path.join('archive', origin, 'custom_commands', file)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Custom command not found')
    # TODO: логировать операцию
    return FileResponse(path, filename=file)

@app.post('/federation/{origin}/push_command')
async def federation_push_command(origin: str, file: UploadFile = File(...)):
    import os
    path = os.path.join('archive', origin, 'custom_commands', file.filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as out_f:
        out_f.write(await file.read())
    # TODO: логировать операцию
    return {'status': 'uploaded', 'file': file.filename}

@app.get('/federation/{origin}/pull_template')
async def federation_pull_template(origin: str, file: str):
    import os
    path = os.path.join('archive', origin, 'templates', file)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Template not found')
    # TODO: логировать операцию
    return FileResponse(path, filename=file)

@app.post('/federation/{origin}/push_template')
async def federation_push_template(origin: str, file: UploadFile = File(...)):
    import os
    path = os.path.join('archive', origin, 'templates', file.filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as out_f:
        out_f.write(await file.read())
    # TODO: логировать операцию
    return {'status': 'uploaded', 'file': file.filename}

# Подключение GraphQL схемы
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get('/backlog')
async def get_backlog(origin: str):
    path = os.path.join('archive', origin, 'federation_backlog.md')
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='backlog not found')
    with open(path, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())

@app.get('/feedback')
async def get_feedback(origin: str):
    path = os.path.join('archive', origin, 'feedback.md')
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='feedback not found')
    with open(path, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())

@app.post('/generate_report')
async def generate_report(context: dict = Body(...)):
    # Заглушка: возвращаем фиктивный отчёт
    return {"report": ["Test report for", context]}

@app.get('/knowledge_package')
async def get_knowledge_package(origin: str, name: str):
    path = os.path.join('archive', origin, 'knowledge_packages', name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Knowledge package not found')
    with open(path, 'r', encoding='utf-8') as f:
        return PlainTextResponse(f.read())

@app.get('/federation/pull_knowledge')
async def federation_pull_knowledge(origin: str, file: str):
    path = os.path.join('archive', origin, 'knowledge_packages', file)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail='Knowledge package not found')
    return FileResponse(path, filename=file)