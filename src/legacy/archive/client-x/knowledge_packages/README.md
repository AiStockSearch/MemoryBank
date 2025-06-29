# Knowledge Snapshots — Инструкция

## Что такое снапшот?
Снапшот — это сохранённая версия кода (компонента, хука, сервиса, конфига) с описанием, тестами, usage и контекстом. Используется для передачи, отката, сравнения, обмена между проектами.

## Где хранятся?
- Все снапшоты хранятся в archive/<origin>/knowledge_packages/ в виде markdown-файлов.
- Для каждого артефакта — отдельный файл с датой и контекстом.

## Как создать снапшот?
- Через CLI:
  ```bash
  python scripts/snapshot_cli.py save --file src/hooks/useMyCustomHook.ts --desc "Для задачи Z" --reason "Откат" --author "Ivan" --project client-x --component useMyCustomHook.ts --tests "// тесты ..." --usage "// usage ..."
  ```
- Вручную: скопировать шаблон snapshot_template.md, заполнить и сохранить как <artifact>-snapshot-<date>.md

## Как восстановить из снапшота?
- Через CLI:
  ```bash
  python scripts/snapshot_cli.py restore --snapshot archive/client-x/knowledge_packages/useMyCustomHook-snapshot-2024-06-20.md --file src/hooks/useMyCustomHook.ts
  ```
- Вручную: скопировать код из блока ``` в нужный файл.

## Best practices
- Всегда указывайте причину, дату, автора и контекст снапшота.
- Для важных изменений — делайте снапшот перед рефакторингом или интеграцией.
- Используйте снапшоты для передачи знаний между origin через federation.
- Храните снапшоты только в knowledge_packages, не смешивайте с рабочим кодом.

## Интеграция с federation
- Снапшоты knowledge_packages экспортируются/импортируются вместе с archive/<origin>/.
- Можно обмениваться снапшотами между проектами через federation endpoints или CLI.

---

**Вопросы и предложения — в backlog или через feedback!** 