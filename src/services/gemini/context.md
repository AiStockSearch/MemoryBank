# context.md

**Назначение:**
Модуль `gemini` реализует асинхронный клиент для работы с Google Gemini API (prompt → completion) и предоставляет типы для интеграции с POP/WebSocket-агентами MCP.

**Структура:**
- client.py — асинхронный клиент
- types.py — типы/интерфейсы
- context.md — описание

**Best practices:**
- Использовать только асинхронные вызовы
- Хранить ключи в .env
- Покрывать тестами все методы 