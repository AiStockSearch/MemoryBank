# context.md

**Назначение:**
Модуль `cursor_rules/` реализует работу с Cursor rules (MDC-формат) для интеграции с системой правил Cursor Editor. Содержит парсер и генератор MDC-файлов, поддерживает frontmatter (YAML) и markdown-тело правила.

**Структура:**
- `mdc_parser.py` — функции для парсинга и генерации MDC-файлов:
  - `parse_mdc_file(filepath)` — парсит MDC-файл, возвращает dict с meta/body.
  - `generate_mdc_file(data)` — генерирует строку MDC-файла из dict.

**Директория .cursor/rules:**
- Хранит project rules в MDC-формате (YAML + markdown).
- Поддерживает вложенность, фильтрацию по scope.

**Дальнейшее развитие:**
- CRUD-операции с MDC-правилами через API.
- Импорт/экспорт zip-архива с правилами.
- Связь с задачами по globs/scope.

**Модули:**
- `mdc_parser.py` — парсер/генератор MDC-файлов.
- `fs_rules.py` — обход .cursor/rules, CRUD-операции с MDC-правилами:
  - `list_rules(base_dir)` — рекурсивно возвращает все правила.
  - `create_rule(meta, body, base_dir, filename)` — создаёт правило.
  - `update_rule(filepath, meta, body)` — обновляет правило.
  - `delete_rule(filepath)` — удаляет правило.
- `export_rules_zip(base_dir)` — экспортирует все MDC-правила в zip-архив (bytes).
- `import_rules_zip(zip_bytes, base_dir)` — импортирует zip-архив с MDC-правилами в директорию.

**REST endpoints:**
- `GET /rules` — список всех правил (.cursor/rules)
- `POST /rules` — создать/обновить правило (MDC)
- `DELETE /rules` — удалить правило по path
- `GET /rules/export` — экспорт всех правил в zip
- `POST /rules/import` — импорт zip-архива правил 