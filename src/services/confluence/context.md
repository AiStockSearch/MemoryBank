# context.md

**Назначение:**
Модуль `confluence` реализует асинхронный клиент для работы с Confluence REST API (чтение, создание, поиск страниц) и предоставляет типы для интеграции с POP/WebSocket-агентами MCP.

**Структура:**
- client.py — асинхронный клиент
- types.py — типы/интерфейсы
- context.md — описание

**Best practices:**
- Использовать только асинхронные вызовы
- Хранить ключи в .env
- Покрывать тестами все методы 