# FastMCP Server — Usage Guide

## Запуск сервера
```bash
pip install fastmcp
python mcp_fastmcp_server.py
```

## Запуск через docker-compose

```bash
docker-compose up --build
```

- FastAPI-сервер будет доступен на http://localhost:8010
- Агент работает в фоне, синхронизирует знания/таски

## Основные возможности
- MCP tools: экспорт, создание задач, federation, обновление правил
- MCP resources: получение backlog, контекста, knowledge packages, feedback
- MCP prompts: генерация отчётов и шаблонов для LLM/агентов

## Основные endpoints (REST)
- GET    /projects/{origin}/export
- GET    /projects/{origin}/backlog
- POST   /projects/{origin}/tasks
- GET    /projects/{origin}/context/{task_id}
- POST   /projects/{origin}/rules
- GET    /projects/{origin}/knowledge/{name}
- GET    /projects/{origin}/feedback
- POST   /projects/{origin}/report

## WebSocket
- ws://localhost:8010/ws/events

## Примеры вызова tools/resources/prompts

### Вызов tool (экспорт проекта)
```python
from fastmcp import FastMCPClient
client = FastMCPClient('http://localhost:8000')
result = client.tool('export_project', origin='client-x')
print(result)
```

### Вызов resource (получение backlog)
```python
result = client.resource('get_backlog', origin='client-x')
print(result['backlog'])
```

### Вызов tool (создание задачи)
```python
result = client.tool('create_task', command='do_something', task_id='123')
print(result)
```

### Вызов prompt (генерация отчёта)
```python
result = client.prompt('generate_report', context={'task_id': '123', 'summary': 'Test'})
print(result)
```

## Пример curl (tool)
```bash
curl -X POST http://localhost:8000/tool/export_project -H 'Content-Type: application/json' -d '{"origin": "client-x"}'
```

## Пример запроса
```bash
curl -X GET http://localhost:8010/projects/cursor/export
```

## Пример WebSocket (Python)
```python
import websockets
import asyncio
async def test():
    async with websockets.connect('ws://localhost:8010/ws/events') as ws:
        await ws.send('ping')
        print(await ws.recv())
asyncio.run(test())
```

## Интеграция с federation
- Для обмена знаниями между серверами реализуй tools/resources типа `federation_pull_knowledge`, `federation_push_knowledge`.
- Используй стандартные методы FastMCP для federation или реализуй свои tools.

## Пример federation_push_knowledge (tool)

### На сервере B (куда загружаем):
```python
@mcp.tool
def federation_push_knowledge(origin: str, file: str, content: str) -> str:
    kp_dir = Path('archive') / origin / 'knowledge_packages'
    kp_dir.mkdir(parents=True, exist_ok=True)
    file_path = kp_dir / file
    file_path.write_text(content, encoding='utf-8')
    return f'Файл {file} успешно загружен в {kp_dir}'
```

### На сервере A (откуда отправляем):
```python
from fastmcp import FastMCPClient
client_b = FastMCPClient('http://localhost:8001', api_key='test-key')
with open('archive/client-x/knowledge_packages/useMyCustomHook-snapshot-2024-06-20.md', 'r', encoding='utf-8') as f:
    content = f.read()
result = client_b.tool('federation_push_knowledge', origin='client-x', file='useMyCustomHook-snapshot-2024-06-20.md', content=content)
print(result)
```

## Аутентификация
- FastMCP поддерживает встроенную аутентификацию (см. [документацию](https://gofastmcp.com/getting-started/welcome)).
- Для production рекомендуется включить auth (API-ключи, JWT, OAuth).
- Для тестов можно запускать без auth.

## Аутентификация (API-ключ)
- При запуске сервера:
  ```python
  mcp = FastMCP('Cursor MCP Server', api_key='your-secret-key')
  ```
- При вызове клиента:
  ```python
  client = FastMCPClient('http://localhost:8000', api_key='your-secret-key')
  ```
- Для production: храните ключи в переменных окружения/CI/CD.

## Best practices
- Все новые endpoints реализуй как @mcp.tool, @mcp.resource, @mcp.prompt.
- Документируй usage для команды.
- Покрывай tools/resources автотестами.
- Используй federation для обмена знаниями между origin.

---

**Вопросы и предложения — в backlog или через feedback!** 