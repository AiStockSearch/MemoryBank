# Глобальный архив проектов (по origin)

В этой папке для каждого origin (project_id) создаётся подпапка с архивными и экспортируемыми данными.

- Не храните здесь шаблоны или активные данные.
- Все federation/import/export — только через archive/<origin>/
- Примеры: mcp, ai-assistant, client-x

**Важно:**
- В archive/<origin>/ хранятся только knowledge packages, changelog, auditLog, projectBrief и другие данные, относящиеся к конкретному origin.
- memory-bank/ используется только как шаблон (template) для новых проектов и не участвует в обмене рабочими или архивными данными.
- Все операции federation, импорт/экспорт, восстановление — только через archive/<origin>/.

