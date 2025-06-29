from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body
from pydantic import BaseModel
from mcp_fastmcp_server import export_project, get_backlog, create_task, get_context, update_rules, federation_pull_knowledge, get_knowledge_package, get_feedback, generate_report
from typing import List

app = FastAPI(title="FastMCP API")

class TaskCreate(BaseModel):
    command: str
    task_id: str

class ReportContext(BaseModel):
    context: dict

# REST endpoints
@app.get("/projects/{origin}/export")
def export(origin: str):
    return {"result": export_project(origin)}

@app.get("/projects/{origin}/backlog")
def backlog(origin: str):
    return get_backlog.call(origin)

@app.post("/projects/{origin}/tasks")
def create_task_api(origin: str, data: TaskCreate = Body(...)):
    return create_task(data.command, data.task_id)

@app.get("/projects/{origin}/context/{task_id}")
def context(origin: str, task_id: str):
    return get_context.call(task_id)

@app.post("/projects/{origin}/rules")
def update_rules_api(origin: str, rules: List[str] = Body(...), user_id: str = Body(...)):
    return update_rules(rules, user_id)

@app.get("/projects/{origin}/knowledge/{name}")
def get_knowledge(origin: str, name: str):
    return get_knowledge_package.call(origin, name)

@app.get("/projects/{origin}/feedback")
def feedback(origin: str):
    return get_feedback.call(origin)

@app.post("/projects/{origin}/report")
def report(origin: str, data: ReportContext):
    return {"report": generate_report.invoke(data.context)}

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