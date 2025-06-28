# Метаданные проектов и шаблонов

В каждом проекте и шаблоне рекомендуется хранить metadata.json с описанием:

- origin: уникальный идентификатор/источник проекта
- owner: владелец или команда
- created: дата создания
- version: версия
- description: краткое описание
- status: active, archived, imported
- source: local, federation, import
- last_updated: дата последнего обновления
- tags: список ключевых тегов

Пример:

	{
	  "origin": "mcp",
	  "owner": "core-team",
	  "created": "2024-06-19",
	  "version": "1.0",
	  "description": "Основной MCP проект для управления задачами и federation.",
	  "status": "active",
	  "source": "local",
	  "last_updated": "2024-06-19",
	  "tags": ["mcp", "ai", "federation"]
	}

