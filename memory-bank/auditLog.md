# auditLog.md

Журнал критичных событий Memory Bank.

## Формат записи
```
[YYYY-MM-DD HH:MM] [USER] [EVENT] <описание>
```

## Примеры
[2024-06-20 13:00] [ivan] [PERMISSION_CHANGE] Назначен новый Team Lead
[2024-06-20 13:10] [devops] [ROLLBACK] Откат до снапшота #42 

---

## [Данные из legacy memory_bank/auditLog.md]

## Автоматизация аудита и AI-логирование

- AI-ассистент автоматически добавляет отчёты, выводы, изменения в auditLog.md и knowledge packages.
- Примеры AI-отчётов: performance checklist, багфикс, оптимизация, AI-генерация summary, презентаций.
- Интеграция с MCP: все изменения фиксируются в MCP, а auditLog.md отражает контекст и историю изменений.
- Автоматизация: при завершении задач, Epic, AI инициирует логирование, архивацию, сравнение версий, аудит изменений. [2025-06-28 23:15] [ERROR] [ai-assistant] Ошибка создания снапшота: Internal Error
[2025-06-28 23:15] [INFO] [ai-assistant] Снапшот создан: snapshot-test.zip
[2025-06-28 23:17] [ERROR] [ai-assistant] Ошибка создания снапшота: Internal Error
[2025-06-28 23:17] [INFO] [ai-assistant] Снапшот создан: snapshot-test.zip
[2025-06-28 23:17] [ERROR] [ai-assistant] Ошибка создания снапшота: Internal Error
[2025-06-28 23:17] [INFO] [ai-assistant] Снапшот создан: snapshot-test.zip
[2025-06-29 00:26] [INFO] [ai-assistant] Экспортировано в PDF: projectBrief.pdf
[2025-06-29 00:26] [INFO] [ai-assistant] Презентация PPTX сгенерирована: projectBrief.pptx
