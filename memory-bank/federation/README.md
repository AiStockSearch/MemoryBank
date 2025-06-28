# Federation (Обмен знаниями)

В этой папке хранятся временные файлы, отчёты и логи, связанные с federation, импортом и экспортом knowledge packages, шаблонов, best practices между проектами и инстансами через MCP/CLI.

**Внимание:** Все операции federation/import/export выполняются только через папку archive/<origin>/ в корне репозитория. Не используйте memory-bank для обмена рабочими или архивными данными.

- Не храните здесь активные или архивные данные проектов.
- Все операции federation требуют подтверждения перед затиранием локальных данных.

## Примеры CLI-команд для federation/import/export

### Экспорт knowledge packages проекта
```bash
mcp federation export --project <origin> --out archive/<origin>/export_<date>.zip
```
- Экспортирует все knowledge packages, шаблоны и best practices указанного origin в архив.

### Импорт knowledge packages в проект
```bash
mcp federation import --file archive/<origin>/export_<date>.zip --project <origin>
```
- Импортирует knowledge packages, шаблоны и best practices в указанный origin. Требует подтверждения перед затиранием локальных данных.

### Аудит импортированных данных
```bash
mcp federation audit --project <origin>
```
- Проверяет метаданные, дубликаты, устаревшие практики, формирует отчёт.

### Просмотр истории federation
```bash
mcp federation log --project <origin>
```
- Показывает историю операций federation/import/export для origin.

---

Best practices:
- Перед импортом делайте бэкап локальных данных.
- Проверяйте метаданные (origin, версия, дата) перед слиянием.
- Все действия логируются в auditLog.md и changelog.

## Шаблоны CLI-команд для federation/import/export

### Экспорт knowledge packages проекта
```bash
mcp federation export --project <project_id> --out federation/export_<project_id>.zip
```
- Экспортирует все knowledge packages, шаблоны и best practices указанного проекта в архив.

### Импорт knowledge packages в проект
```bash
mcp federation import --file federation/export_<project_id>.zip --project <project_id>
```
- Импортирует knowledge packages, шаблоны и best practices в указанный проект. Требует подтверждения перед затиранием локальных данных.

### Аудит импортированных данных
```bash
mcp federation audit --project <project_id>
```
- Проверяет метаданные, дубликаты, устаревшие практики, формирует отчёт.

### Просмотр истории federation
```bash
mcp federation log --project <project_id>
```
- Показывает историю операций federation/import/export для проекта.

> Все действия federation логируются в auditLog.md и changelog. Перед импортом рекомендуется делать бэкап локальных данных.

