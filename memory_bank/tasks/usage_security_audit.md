# Инструкция по использованию security_audit.py

## Назначение
Скрипт автоматизирует аудит безопасности проекта по чек-листу (memory_bank/security_audit_checklist.md), логирует результаты, отправляет уведомления и может создавать задачи в GitHub Issues или Jira по найденным проблемам.

## Переменные окружения
- **SECURITY_AUDIT_MODE** — режим аудита (full, fast, custom)
- **SLACK_WEBHOOK_URL** — для уведомлений в Slack
- **EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS** — для email-уведомлений
- **GITHUB_TOKEN, GITHUB_REPO** — для создания задач по найденным проблемам в GitHub Issues (owner/repo)
- **JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT** — для создания задач по найденным проблемам в Jira

## Запуск
```bash
python memory_bank/tasks/security_audit.py
```

## Сценарии использования
- Проверка всех пунктов чек-листа (конфиги, зависимости, секреты, права)
- Логирование результатов в archive/<origin>/auditLog.md
- Создание задач по найденным проблемам (GitHub/Jira/print)
- Уведомления в Slack/email/print о результатах аудита

## Интеграция с таск-трекерами
- **GitHub Issues:**
  - Экспортируйте GITHUB_TOKEN и GITHUB_REPO
- **Jira:**
  - Экспортируйте JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT
- Если переменные не заданы — задачи выводятся в консоль

## Интеграция с уведомлениями
- **Slack:**
  - Экспортируйте SLACK_WEBHOOK_URL
- **Email:**
  - Экспортируйте EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- Если переменные не заданы — уведомления выводятся в консоль

## Типовые ошибки
- Отсутствие чек-листа — аудит пропускается
- Ошибки интеграции с API — выводятся в консоль
- Некорректные переменные окружения — fallback на print

## Best practices
- Регулярно запускать аудит (cron, CI/CD)
- Использовать только валидные токены и ключи
- Проверять результаты в auditLog.md и backlog 