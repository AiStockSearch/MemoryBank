from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from pydantic import BaseModel
from mcp_fastmcp_server import export_project, get_backlog, create_task, get_context, update_rules, federation_pull_knowledge, get_knowledge_package, get_feedback, generate_report
from typing import List
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status

app = FastAPI(title="FastMCP API")

class TaskCreate(BaseModel):
    command: str
    task_id: str

class ReportContext(BaseModel):
    context: dict

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

@app.post("/projects/{origin}/tasks")
def create_task_api(origin: str, data: TaskCreate = Body(...)):
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

@app.post("/projects/{origin}/report")
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
            await manager.broadcast(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "type": type(exc).__name__}
    ) 