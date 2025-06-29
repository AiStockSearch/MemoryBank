# memory_bank/tasks/ — Автоматизация и задачи

## Назначение
Скрипты и шаблоны для автоматизации рутинных задач, сбора обратной связи, интеграции с таск-трекерами, аудита и поддержки процессов MCP/Federation.

## Структура
- `auto_feedback_to_backlog.py` — автоматизация сбора и переноса feedback, уведомления, интеграция с GitHub/Jira, отчётность
- `test_auto_feedback_to_backlog.py` — автотесты для основного скрипта (pytest)
- `usage_auto_feedback_to_backlog.md` — подробная инструкция по использованию и интеграции
- `security_audit.py` — автоматизация аудита безопасности по чек-листу, логирование, интеграция с таск-трекером
- `usage_security_audit.md` — usage-инструкция по security audit
- другие шаблоны и утилиты для аудита, onboarding, безопасности

## Автотесты
- Запуск: `pytest memory_bank/tasks/test_auto_feedback_to_backlog.py`
- Покрытие: добавление feedback, фильтрация, логирование, интеграция, отчётность

## Best practices
- Все переменные окружения для интеграций и секретов — только через .env или CI/CD
- Не хранить реальные токены/ключи в коде
- Регулярно запускать автотесты и проверять отчёты
- Использовать usage-инструкции для каждого скрипта

## Рекомендации по CI/CD
- Настроить автозапуск скриптов по расписанию (cron) или при изменении feedback
- Интегрировать автотесты в pipeline (GitHub Actions, GitLab CI и др.)
- Хранить отчёты и логи в archive/
- Для security audit — запускать после каждого релиза или обновления зависимостей

## Usage-инструкции
- [auto_feedback_to_backlog.md](usage_auto_feedback_to_backlog.md)
- [usage_security_audit.md](usage_security_audit.md)

---

**Вопросы, предложения и новые задачи — через feedback.md или напрямую в backlog!** 