from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from cacd import CACD
from typing import Optional
import json
from fastapi.responses import HTMLResponse
import logging

app = FastAPI()
cacd = CACD()

API_KEY = "supersecretkey"  # Можно вынести в переменные окружения

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

def verify_api_key(request: Request):
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

class TaskRequest(BaseModel):
    command: str
    task_id: str

class RuleRequest(BaseModel):
    rules: list

@app.post('/tasks', dependencies=[Depends(verify_api_key)])
async def create_task(req: TaskRequest):
    logger.info(f"Создание задачи: {req.task_id}")
    task = await cacd.process_command(req.command, req.task_id)
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