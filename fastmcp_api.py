from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from pydantic import BaseModel, Field
from mcp_fastmcp_server import export_project, get_backlog, create_task, get_context, update_rules, federation_pull_knowledge, get_knowledge_package, get_feedback, generate_report
from typing import List
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
import json
from openai_client import call_openai

app = FastAPI(title="FastMCP API")

class TaskCreate(BaseModel):
    command: str = Field(..., description="Команда для задачи", example="test")
    task_id: str = Field(..., description="ID задачи", example="test-001")

class ReportContext(BaseModel):
    context: dict = Field(..., description="Контекст для генерации отчёта", example={"task_id": "test-001", "summary": "test"})

# REST endpoints
@app.get("/projects/{origin}/export")
def export(origin: str):
    print('DEBUG export_project:', type(export_project), export_project)
    return {"result": export_project.fn(origin)}

@app.get("/projects/{origin}/backlog")
def backlog(origin: str):
    print('DEBUG get_backlog:', type(get_backlog), get_backlog)
    result = get_backlog.fn(origin)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result

@app.post("/projects/{origin}/tasks", summary="Создать задачу", description="Создаёт новую задачу для проекта.")
def create_task_api(
    origin: str,
    data: TaskCreate = Body(...)
):
    print('DEBUG create_task:', type(create_task), create_task)
    return create_task.fn(data.command, data.task_id)

@app.get("/projects/{origin}/context/{task_id}")
def context(origin: str, task_id: str):
    print('DEBUG get_context:', type(get_context), get_context)
    return get_context.fn(task_id)

@app.post("/projects/{origin}/rules")
def update_rules_api(origin: str, rules: List[str] = Body(...), user_id: str = Body(...)):
    return update_rules(rules, user_id)

@app.get("/projects/{origin}/knowledge/{name}")
def get_knowledge(origin: str, name: str):
    print('DEBUG get_knowledge_package:', type(get_knowledge_package), get_knowledge_package)
    result = get_knowledge_package.fn(origin, name)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result

@app.get("/projects/{origin}/feedback")
def feedback(origin: str):
    print('DEBUG get_feedback:', type(get_feedback), get_feedback)
    result = get_feedback.fn(origin)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result

@app.post("/projects/{origin}/report", summary="Сгенерировать отчёт", description="Генерирует отчёт по задаче на основе контекста.")
def report(origin: str, data: ReportContext):
    print('DEBUG generate_report:', type(generate_report), generate_report)
    return {"report": generate_report.fn(data.context)}

# WebSocket для событий (минимальный пример)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except Exception:
                response = {"Echo": data}
                print('RECV (raw):', data)
                print('SEND:', response)
                await manager.broadcast(json.dumps(response))
                continue
            cmd = msg.get("cmd")
            text = msg.get("text")
            # Рекурсивно парсить text, пока это JSON с result
            while True:
                try:
                    text_obj = json.loads(text)
                    if isinstance(text_obj, dict) and "result" in text_obj:
                        text = text_obj["result"]
                    else:
                        break
                except Exception:
                    break
            # Ответ формируем строго по текущему cmd
            if cmd == "generate":
                response = {"role": "gen", "result": f"generated: {text}"}
            elif cmd == "analyze":
                response = {"role": "analyze", "result": f"analyzed: {text}"}
            elif cmd == "confirm":
                response = {"role": "confirm", "result": f"confirmed: {text}"}
            elif cmd == "broadcast":
                response = {"role": "broadcast", "result": f"broadcast: {text}"}
            elif cmd == "summarize":
                response = {"role": "llm", "result": f"summary: {text}"}
            elif cmd == "openai":
                # POP-агент для OpenAI
                prompt = msg.get("prompt") or text
                model = msg.get("model", "gpt-3.5-turbo")
                max_tokens = msg.get("max_tokens", 512)
                temperature = msg.get("temperature", 0.7)
                try:
                    llm_resp = await call_openai(prompt, model, max_tokens, temperature)
                    response = {"role": "llm_openai", "result": llm_resp}
                except Exception as e:
                    response = {"error": str(e)}
            else:
                response = {"error": "unknown command"}
            print('RECV:', msg)
            print('SEND:', response)
            await manager.broadcast(json.dumps(response))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "type": type(exc).__name__}
    ) 