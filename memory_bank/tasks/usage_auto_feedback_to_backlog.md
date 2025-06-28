# Инструкция по использованию auto_feedback_to_backlog.py

## Назначение
Скрипт автоматизирует перенос новых валидных feedback из archive/<origin>/feedback.md в archive/<origin>/federation_backlog.md, логирует действия, отправляет уведомления и может создавать задачи в GitHub Issues или Jira.

## Переменные окружения
- **SLACK_WEBHOOK_URL** — для уведомлений в Slack
- **EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS** — для email-уведомлений
- **GITHUB_TOKEN, GITHUB_REPO** — для создания задач в GitHub Issues (owner/repo)
- **JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT** — для создания задач в Jira

## Запуск
```bash
python memory_bank/tasks/auto_feedback_to_backlog.py
```

## Сценарии использования
- Переносит только новые и валидные feedback (минимум 10 символов, не технические строки).
- Для каждого нового feedback:
  - Добавляет в backlog
  - Логирует в auditLog.md
  - Отправляет уведомление (Slack/email/print)
  - Создаёт задачу в GitHub/Jira (если настроено)
- Генерирует summary-отчёт в archive/feedback_report.md

## Интеграция с таск-трекерами
- **GitHub Issues:**
  - Экспортируйте GITHUB_TOKEN и GITHUB_REPO
- **Jira:**
  - Экспортируйте JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT
- Если переменные не заданы — задачи выводятся в консоль

## Тестирование
- Автотесты: `pytest memory_bank/tasks/test_auto_feedback_to_backlog.py`
- Используется monkeypatch для mock-интеграций

## Типовые ошибки
- Отсутствие нужных файлов (feedback.md, federation_backlog.md) — origin пропускается
- Ошибки интеграции с API — выводятся в консоль
- Некорректные переменные окружения — fallback на print

## Рекомендации
- Настроить автозапуск через cron или CI/CD
- Регулярно проверять feedback_report.md и auditLog.md
- Использовать только валидные токены и ключи 