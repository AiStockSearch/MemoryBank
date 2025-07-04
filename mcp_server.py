from fastapi import FastAPI, HTTPException, Depends, Request, Query, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Header
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
import tempfile
import shutil
import datetime
import subprocess
import glob

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
        # Копируем глобальные правила
        global_rules = await conn.fetch('SELECT * FROM cursor_rules WHERE project_id IS NULL')
        for rule in global_rules:
            await conn.execute(
                'INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)',
                rule["id"] + f"_{project_id}", project_id, rule["type"], rule["value"], rule["description"]
            )
        # Инициализация дефолтных шаблонов (аналогично можно сделать для глобальных шаблонов)
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
async def export_project(project_id: int, user_id: str = Header(None, alias="X-USER-ID")):
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
            'INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)',
            project_id, user_id, 'export', json.dumps({'files': ['tasks.json', 'rules.json', 'templates.json', 'embeddings.json', 'docs.json', 'history.json']})
        )

    # Push-уведомление
    msg = f"Проект {project_id} экспортирован в архив"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)

    return StreamingResponse(zip_buffer, media_type='application/zip', headers={
        'Content-Disposition': f'attachment; filename="project_{project_id}_export.zip"'
    })

@app.post('/projects/{project_id}/merge', dependencies=[Depends(verify_api_key)])
async def merge_project(
    project_id: int,
    file: UploadFile = File(...),
    dry_run: bool = Form(False),
    user_id: str = Header(None, alias="X-USER-ID")
):
    """
    Сливает zip-архив с существующим проектом. Dry-run — только diff, иначе применяет изменения.
    Вложенные файлы docs сохраняются во временную папку docs/temp/.
    """
    # 1. Распаковываем архив во временную папку
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, 'import.zip')
        with open(zip_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(tmpdir)

        # 2. Читаем json-файлы
        def read_json(name):
            path = os.path.join(tmpdir, name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        import_tasks = read_json('tasks.json')
        import_rules = read_json('rules.json')
        import_templates = read_json('templates.json')
        import_embeddings = read_json('embeddings.json')
        import_docs = read_json('docs.json')
        import_history = read_json('history.json')

        # 3. Получаем текущие данные
        tasks = await cacd.memory.get_all_tasks(project_id)
        rules = await cacd.memory.get_all_rules(project_id)
        templates = await cacd.memory.get_all_templates(project_id)
        embeddings = await cacd.memory.get_all_embeddings(project_id)
        docs = await cacd.memory.get_all_docs(project_id)
        history = await cacd.memory.get_all_history(project_id)

        # 4. Формируем diff по id (или уникальным полям)
        def diff_by_id(current, incoming, key='id'):
            current_map = {str(x[key]): x for x in current}
            incoming_map = {str(x[key]): x for x in incoming}
            added = [x for k, x in incoming_map.items() if k not in current_map]
            updated = [x for k, x in incoming_map.items() if k in current_map and x != current_map[k]]
            conflicted = [
                {'id': k, 'current': current_map[k], 'incoming': incoming_map[k]}
                for k in incoming_map if k in current_map and incoming_map[k] != current_map[k]
            ]
            skipped = [x for k, x in current_map.items() if k in incoming_map and incoming_map[k] == x]
            return {'added': added, 'updated': updated, 'conflicted': conflicted, 'skipped': skipped}

        tasks_diff = diff_by_id(tasks, import_tasks, 'id')
        rules_diff = diff_by_id(rules, import_rules, 'id')
        templates_diff = diff_by_id(templates, import_templates, 'id')
        embeddings_diff = diff_by_id(embeddings, import_embeddings, 'id')
        docs_diff = diff_by_id(docs, import_docs, 'id')
        history_diff = diff_by_id(history, import_history, 'id')

        # 5. Вложенные файлы (docs/attachments)
        docs_dir = os.path.join('docs', 'temp')
        os.makedirs(docs_dir, exist_ok=True)
        files_in_zip = [f for f in zipf.namelist() if not f.endswith('.json')]
        extracted_files = []
        for fname in files_in_zip:
            src = os.path.join(tmpdir, fname)
            dst = os.path.join(docs_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                extracted_files.append(fname)

        # 6. Если dry_run — только diff
        if dry_run:
            return {
                'tasks': tasks_diff,
                'rules': rules_diff,
                'templates': templates_diff,
                'embeddings': embeddings_diff,
                'docs': docs_diff,
                'history': history_diff,
                'attachments': extracted_files
            }

        # 7. Применяем изменения (только added, обновления — по отдельному запросу)
        pool = await cacd.memory._get_pool()
        async with pool.acquire() as conn:
            # Добавляем только новые задачи, правила, шаблоны, docs, embeddings, history
            for t in tasks_diff['added']:
                await conn.execute('''INSERT INTO tasks (id, project_id, command, context, rules, status, result) VALUES ($1, $2, $3, $4, $5, $6, $7)''',
                    t['id'], project_id, t.get('command'), t.get('context'), json.dumps(t.get('rules')), t.get('status'), t.get('result'))
            for r in rules_diff['added']:
                await conn.execute('''INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)''',
                    r['id'], project_id, r.get('type'), r.get('value'), r.get('description'))
            for tpl in templates_diff['added']:
                await conn.execute('''INSERT INTO templates (project_id, name, repo_url, tags) VALUES ($1, $2, $3, $4)''',
                    project_id, tpl.get('name'), tpl.get('repo_url'), tpl.get('tags'))
            for emb in embeddings_diff['added']:
                await conn.execute('''INSERT INTO embeddings (project_id, task_id, vector, description) VALUES ($1, $2, $3, $4)''',
                    project_id, emb.get('task_id'), emb.get('vector'), emb.get('description'))
            for d in docs_diff['added']:
                await conn.execute('''INSERT INTO docs (project_id, type, content) VALUES ($1, $2, $3)''',
                    project_id, d.get('type'), d.get('content'))
            for h in history_diff['added']:
                await conn.execute('''INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)''',
                    project_id, user_id, h.get('action'), json.dumps(h.get('details')))

        # 8. Логируем merge
        msg = f"Merge архива в проект {project_id} завершён. Добавлено: задачи {len(tasks_diff['added'])}, правила {len(rules_diff['added'])}, шаблоны {len(templates_diff['added'])}, docs {len(docs_diff['added'])}, embeddings {len(embeddings_diff['added'])}, history {len(history_diff['added'])}"
        await notify_ws_clients(msg)
        notify_mac("MCP", msg)

        return {
            'status': 'merged',
            'added': {
                'tasks': len(tasks_diff['added']),
                'rules': len(rules_diff['added']),
                'templates': len(templates_diff['added']),
                'embeddings': len(embeddings_diff['added']),
                'docs': len(docs_diff['added']),
                'history': len(history_diff['added']),
                'attachments': extracted_files
            },
            'conflicts': {
                'tasks': tasks_diff['conflicted'],
                'rules': rules_diff['conflicted'],
                'templates': templates_diff['conflicted'],
                'embeddings': embeddings_diff['conflicted'],
                'docs': docs_diff['conflicted'],
                'history': history_diff['conflicted']
            }
        }

@app.post('/projects/import', dependencies=[Depends(verify_api_key)])
async def import_project(
    file: UploadFile = File(...),
    new_origin: str = Form(None),
    user_id: str = Header(None, alias="X-USER-ID")
):
    """
    Импортирует zip-архив как новый проект. Если origin уже есть — возвращает ошибку или предлагает переименовать.
    Вложенные файлы docs сохраняются в docs/.
    """
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, 'import.zip')
        with open(zip_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(tmpdir)

        def read_json(name):
            path = os.path.join(tmpdir, name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        import_tasks = read_json('tasks.json')
        import_rules = read_json('rules.json')
        import_templates = read_json('templates.json')
        import_embeddings = read_json('embeddings.json')
        import_docs = read_json('docs.json')
        import_history = read_json('history.json')

        # Получаем origin из одного из файлов (например, rules или tasks)
        origin = None
        if import_rules and 'origin' in import_rules[0]:
            origin = import_rules[0]['origin']
        elif import_tasks and 'origin' in import_tasks[0]:
            origin = import_tasks[0]['origin']
        if new_origin:
            origin = new_origin
        if not origin:
            origin = f"imported_{os.urandom(4).hex()}"

        # Проверяем уникальность origin
        pool = await cacd.memory._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow('SELECT id FROM projects WHERE origin = $1', origin)
            if row:
                raise HTTPException(status_code=409, detail=f"Project with origin '{origin}' already exists. Укажите новый origin.")
            # Создаём новый проект
            project_row = await conn.fetchrow(
                'INSERT INTO projects (name, description, origin) VALUES ($1, $2, $3) RETURNING id',
                f"Импортированный проект {origin}", "Импорт через API", origin
            )
            project_id = project_row['id']
            # Импортируем все сущности с новым project_id
            for t in import_tasks:
                await conn.execute('''INSERT INTO tasks (id, project_id, command, context, rules, status, result) VALUES ($1, $2, $3, $4, $5, $6, $7)''',
                    t['id'], project_id, t.get('command'), t.get('context'), json.dumps(t.get('rules')), t.get('status'), t.get('result'))
            for r in import_rules:
                await conn.execute('''INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)''',
                    r['id'], project_id, r.get('type'), r.get('value'), r.get('description'))
            for tpl in import_templates:
                await conn.execute('''INSERT INTO templates (project_id, name, repo_url, tags) VALUES ($1, $2, $3, $4)''',
                    project_id, tpl.get('name'), tpl.get('repo_url'), tpl.get('tags'))
            for emb in import_embeddings:
                await conn.execute('''INSERT INTO embeddings (project_id, task_id, vector, description) VALUES ($1, $2, $3, $4)''',
                    project_id, emb.get('task_id'), emb.get('vector'), emb.get('description'))
            for d in import_docs:
                await conn.execute('''INSERT INTO docs (project_id, type, content) VALUES ($1, $2, $3)''',
                    project_id, d.get('type'), d.get('content'))
            for h in import_history:
                await conn.execute('''INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)''',
                    project_id, user_id, h.get('action'), json.dumps(h.get('details')))

        # Вложенные файлы (docs/attachments)
        docs_dir = os.path.join('docs')
        os.makedirs(docs_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            files_in_zip = [f for f in zipf.namelist() if not f.endswith('.json')]
            extracted_files = []
            for fname in files_in_zip:
                src = os.path.join(tmpdir, fname)
                dst = os.path.join(docs_dir, fname)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    extracted_files.append(fname)

        msg = f"Импортирован новый проект {origin} (id={project_id}). Задач: {len(import_tasks)}, правил: {len(import_rules)}, docs: {len(import_docs)}"
        await notify_ws_clients(msg)
        notify_mac("MCP", msg)
        return {
            'status': 'imported',
            'project_id': project_id,
            'origin': origin,
            'added': {
                'tasks': len(import_tasks),
                'rules': len(import_rules),
                'templates': len(import_templates),
                'embeddings': len(import_embeddings),
                'docs': len(import_docs),
                'history': len(import_history),
                'attachments': extracted_files
            }
        }

@app.post('/projects/{project_id}/snapshot', dependencies=[Depends(verify_api_key)])
async def create_snapshot(project_id: int, user_id: str = Header(None, alias="X-USER-ID")):
    """
    Создаёт снапшот проекта: экспортирует архив, делает git commit и tag, пишет в changelog/history.
    """
    # 1. Экспортируем проект в zip
    tasks = await cacd.memory.get_all_tasks(project_id)
    rules = await cacd.memory.get_all_rules(project_id)
    templates = await cacd.memory.get_all_templates(project_id)
    embeddings = await cacd.memory.get_all_embeddings(project_id)
    docs = await cacd.memory.get_all_docs(project_id)
    history = await cacd.memory.get_all_history(project_id)
    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
    archive_name = f'project_{project_id}_snapshot_{now}.zip'
    archive_path = os.path.join('docs', archive_name)
    import io, zipfile
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('tasks.json', json.dumps(tasks, ensure_ascii=False, indent=2))
        zipf.writestr('rules.json', json.dumps(rules, ensure_ascii=False, indent=2))
        zipf.writestr('templates.json', json.dumps(templates, ensure_ascii=False, indent=2))
        zipf.writestr('embeddings.json', json.dumps(embeddings, ensure_ascii=False, indent=2))
        zipf.writestr('docs.json', json.dumps(docs, ensure_ascii=False, indent=2))
        zipf.writestr('history.json', json.dumps(history, ensure_ascii=False, indent=2))
    with open(archive_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    # 2. Git commit и tag
    commit_msg = f"[snapshot] project {project_id} at {now}"
    tag = f"snapshot-{project_id}-{now}"
    try:
        subprocess.run(["git", "add", archive_path], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "tag", tag], check=True)
    except Exception as e:
        print(f"Git error: {e}")
    # 3. Запись в history/changelog
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)',
            project_id, user_id, 'snapshot', json.dumps({'archive': archive_name, 'tag': tag, 'date': now})
        )
    msg = f"Создан снапшот проекта {project_id}: {archive_name}, git tag: {tag}"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "snapshot_created", "archive": archive_name, "tag": tag}

@app.post('/projects/{project_id}/restore_snapshot', dependencies=[Depends(verify_api_key)])
async def restore_snapshot(project_id: int, tag: str, user_id: str = Header(None, alias="X-USER-ID")):
    """
    Восстанавливает проект из git snapshot/tag: ищет архив, импортирует его через merge.
    """
    import subprocess
    import glob
    # 1. git checkout tag (только docs/)
    try:
        subprocess.run(["git", "checkout", tag, "--", "docs/"], check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git checkout error: {e}")
    # 2. Ищем архив снапшота
    pattern = f"docs/project_{project_id}_snapshot_*.zip"
    files = glob.glob(pattern)
    if not files:
        raise HTTPException(status_code=404, detail="Snapshot archive not found for this tag")
    archive_path = max(files, key=os.path.getctime)  # последний по времени
    # 3. Импортируем архив через merge
    from fastapi import UploadFile
    class DummyUploadFile:
        def __init__(self, path):
            self.file = open(path, 'rb')
            self.filename = os.path.basename(path)
    upload = DummyUploadFile(archive_path)
    resp = await merge_project(project_id, file=upload, dry_run=False, user_id=user_id)
    upload.file.close()
    return {"status": "restored", "archive": archive_path, "merge_result": resp}

@app.post('/projects/{project_id}/rollback', dependencies=[Depends(verify_api_key)])
async def rollback_project(project_id: int, tag: str = None, user_id: str = Header(None, alias="X-USER-ID")):
    """
    Откатывает проект к предыдущему снапшоту (или к указанному git tag).
    Записывает событие rollback в history/changelog.
    """
    import subprocess
    import glob
    # 1. Находим нужный tag (если не указан — предыдущий по времени)
    if not tag:
        # Получаем все snapshot-теги для проекта
        result = subprocess.run(["git", "tag"], capture_output=True, text=True)
        tags = [t for t in result.stdout.splitlines() if t.startswith(f"snapshot-{project_id}-")]
        tags.sort(reverse=True)
        if len(tags) < 2:
            raise HTTPException(status_code=404, detail="Нет предыдущих снапшотов для отката")
        tag = tags[1]  # предыдущий (до последнего)
    # 2. Восстанавливаем через restore_snapshot
    resp = await restore_snapshot(project_id, tag, user_id)
    # 3. Запись в history/changelog
    pool = await cacd.memory._get_pool()
    import datetime
    now = datetime.datetime.utcnow().isoformat()
    async with pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO history (project_id, user_id, action, details) VALUES ($1, $2, $3, $4)',
            project_id, user_id, 'rollback', json.dumps({'tag': tag, 'date': now, 'result': resp})
        )
    msg = f"Откат проекта {project_id} к снапшоту {tag} завершён"
    await notify_ws_clients(msg)
    notify_mac("MCP", msg)
    return {"status": "rollback_done", "tag": tag, "result": resp}

@app.get('/history')
async def get_history(
    project_id: Optional[int] = Query(None),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100)
) -> List[dict]:
    """
    Возвращает историю событий с фильтрацией по проекту, пользователю, действию, дате.
    """
    pool = await cacd.memory._get_pool()
    query = 'SELECT * FROM history WHERE 1=1'
    params = []
    if project_id:
        query += ' AND project_id = $' + str(len(params)+1)
        params.append(project_id)
    if user_id:
        query += ' AND user_id = $' + str(len(params)+1)
        params.append(user_id)
    if action:
        query += ' AND action = $' + str(len(params)+1)
        params.append(action)
    if date_from:
        query += ' AND created_at >= $' + str(len(params)+1)
        params.append(date_from)
    if date_to:
        query += ' AND created_at <= $' + str(len(params)+1)
        params.append(date_to)
    query += ' ORDER BY created_at DESC LIMIT $' + str(len(params)+1)
    params.append(limit)
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

@app.post('/files/upload', dependencies=[Depends(verify_api_key)])
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    user_id: str = Header(None, alias="X-USER-ID")
):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_path = f"docs/{file.filename}"
    s3_url = None
    # Загрузка в S3/minio если настроено
    if S3_ENDPOINT and S3_ACCESS_KEY and S3_SECRET_KEY and S3_BUCKET:
        s3 = boto3.client('s3', endpoint_url=S3_ENDPOINT, aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
        s3.put_object(Bucket=S3_BUCKET, Key=file.filename, Body=content)
        s3_url = f"{S3_ENDPOINT}/{S3_BUCKET}/{file.filename}"
    else:
        with open(file_path, 'wb') as f:
            f.write(content)
    # Определяем версию
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        vrow = await conn.fetchrow('SELECT max(version) as v FROM file_versions WHERE file_path = $1 AND project_id = $2', file.filename, project_id)
        version = (vrow['v'] or 0) + 1
        await conn.execute('''INSERT INTO file_versions (project_id, file_path, version, hash, user_id, s3_url) VALUES ($1, $2, $3, $4, $5, $6)''',
            project_id, file.filename, version, file_hash, user_id, s3_url)
    return {"status": "uploaded", "file": file.filename, "version": version, "s3_url": s3_url}

@app.get('/files/versions')
async def get_file_versions(project_id: int, file_path: str):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT version, hash, user_id, s3_url, created_at FROM file_versions WHERE project_id = $1 AND file_path = $2 ORDER BY version DESC', project_id, file_path)
        return [{"version": r["version"], "hash": r["hash"], "user_id": r["user_id"], "s3_url": r["s3_url"], "created_at": r["created_at"]} for r in rows]

@app.post('/files/rollback')
async def rollback_file(project_id: int, file_path: str, version: int, user_id: str = Header(None, alias="X-USER-ID")):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT hash, s3_url FROM file_versions WHERE project_id = $1 AND file_path = $2 AND version = $3', project_id, file_path, version)
        if not row:
            raise HTTPException(status_code=404, detail="Версия файла не найдена")
        # Восстанавливаем файл из S3 или локально
        if row['s3_url']:
            import requests
            resp = requests.get(row['s3_url'])
            content = resp.content
        else:
            with open(f"docs/{file_path}", 'rb') as f:
                content = f.read()
        # Перезаписываем файл
        with open(f"docs/{file_path}", 'wb') as f:
            f.write(content)
        # Сохраняем новую версию (rollback)
        vrow = await conn.fetchrow('SELECT max(version) as v FROM file_versions WHERE file_path = $1 AND project_id = $2', file_path, project_id)
        new_version = (vrow['v'] or 0) + 1
        await conn.execute('''INSERT INTO file_versions (project_id, file_path, version, hash, user_id, s3_url) VALUES ($1, $2, $3, $4, $5, $6)''',
            project_id, file_path, new_version, row['hash'], user_id, row['s3_url'])
    return {"status": "rolled_back", "file": file_path, "version": version}

@app.post('/embeddings/add', dependencies=[Depends(verify_api_key)])
async def add_embedding(
    project_id: int,
    entity_id: str,
    entity_type: str,  # 'task' | 'doc' | 'template'
    vector: list[float],
    model: str,
    description: str = '',
    user_id: str = Header(None, alias="X-USER-ID")
):
    # Проверка размерности (пример: 384)
    if len(vector) not in (384, 768, 1024):
        raise HTTPException(status_code=400, detail="Неподдерживаемая размерность эмбеддинга")
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO embeddings (project_id, task_id, vector, description) VALUES ($1, $2, $3, $4)''',
            project_id, entity_id, vector, description
        )
    return {"status": "embedding_added", "entity_id": entity_id, "type": entity_type, "model": model}

@app.post('/embeddings/search', dependencies=[Depends(verify_api_key)])
async def search_embeddings(
    project_id: int,
    vector: list[float] = None,
    entity_type: str = None,
    entity_id: str = None,
    top_k: int = 5
) -> list[Any]:
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        # Если передан entity_id — ищем его вектор
        if entity_id:
            row = await conn.fetchrow('SELECT vector FROM embeddings WHERE project_id = $1 AND task_id = $2', project_id, entity_id)
            if not row:
                raise HTTPException(status_code=404, detail="Эмбеддинг не найден")
            vector = row['vector']
        if not vector:
            raise HTTPException(status_code=400, detail="Не передан вектор для поиска")
        # Поиск по pgvector (cosine distance)
        query = 'SELECT task_id, vector, description FROM embeddings WHERE project_id = $1'
        params = [project_id]
        if entity_type:
            query += ' AND description LIKE $2'
            params.append(f'%{entity_type}%')
        query += ' ORDER BY vector <#> $' + str(len(params)+1) + ' LIMIT $' + str(len(params)+2)
        params.append(vector)
        params.append(top_k)
        rows = await conn.fetch(query, *params)
        return [{"entity_id": r["task_id"], "vector": r["vector"], "description": r["description"]} for r in rows]

@app.post('/embeddings/cluster', dependencies=[Depends(verify_api_key)])
async def cluster_embeddings(
    project_id: int,
    entity_type: str = None,
    n_clusters: int = 5
):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        query = 'SELECT task_id, vector, description FROM embeddings WHERE project_id = $1'
        params = [project_id]
        if entity_type:
            query += ' AND description LIKE $2'
            params.append(f'%{entity_type}%')
        rows = await conn.fetch(query, *params)
        if not rows or len(rows) < n_clusters:
            raise HTTPException(status_code=400, detail="Недостаточно эмбеддингов для кластеризации")
        X = np.array([r['vector'] for r in rows])
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        clusters = {}
        for idx, r in enumerate(rows):
            l = int(labels[idx])
            clusters.setdefault(l, []).append({"entity_id": r["task_id"], "description": r["description"]})
        return {"clusters": clusters, "centroids": kmeans.cluster_centers_.tolist()}

@app.post('/embeddings/recommend', dependencies=[Depends(verify_api_key)])
async def recommend_embeddings(
    project_id: int,
    entity_id: str = None,
    vector: list[float] = None,
    entity_type: str = None,
    top_k: int = 5
):
    # Использует /embeddings/search для поиска похожих, но фильтрует по entity_type
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        if entity_id:
            row = await conn.fetchrow('SELECT vector FROM embeddings WHERE project_id = $1 AND task_id = $2', project_id, entity_id)
            if not row:
                raise HTTPException(status_code=404, detail="Эмбеддинг не найден")
            vector = row['vector']
        if not vector:
            raise HTTPException(status_code=400, detail="Не передан вектор для рекомендации")
        query = 'SELECT task_id, vector, description FROM embeddings WHERE project_id = $1'
        params = [project_id]
        if entity_type:
            query += ' AND description LIKE $2'
            params.append(f'%{entity_type}%')
        query += ' ORDER BY vector <#> $' + str(len(params)+1) + ' LIMIT $' + str(len(params)+2)
        params.append(vector)
        params.append(top_k)
        rows = await conn.fetch(query, *params)
        return [{"entity_id": r["task_id"], "description": r["description"]} for r in rows]

@app.get('/rules/global', dependencies=[Depends(verify_api_key)])
async def get_global_rules():
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM cursor_rules WHERE project_id IS NULL')
        return [dict(row) for row in rows]

@app.post('/rules/global', dependencies=[Depends(verify_api_key)])
async def update_global_rules(rules: list, user_id: str = Header(None, alias="X-USER-ID")):
    pool = await cacd.memory._get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM cursor_rules WHERE project_id IS NULL')
        for rule in rules:
            await conn.execute(
                'INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, NULL, $2, $3, $4)',
                rule["id"], rule["type"], rule["value"], rule.get("description", "")
            )
        # Логируем изменение глобальных правил
        await conn.execute(
            'INSERT INTO history (project_id, user_id, action, details) VALUES (NULL, $1, $2, $3)',
            user_id, 'update_global_rules', json.dumps({'rules': rules})
        )
    return {"status": "global_rules_updated"} 
