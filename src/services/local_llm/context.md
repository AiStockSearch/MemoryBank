# context.md

**Назначение:**
Модуль `local_llm` реализует асинхронный универсальный клиент для работы с локальными LLM (Ollama, LM Studio, Llama.cpp, HuggingFace Inference API) и предоставляет типы для интеграции с POP/WebSocket-агентами MCP.

**Структура:**
- client.py — асинхронный клиент
- types.py — типы/интерфейсы
- context.md — описание

**Best practices:**
- Использовать только асинхронные вызовы
- Конфигурировать endpoint и ключи через .env/config
- Покрывать тестами все методы 