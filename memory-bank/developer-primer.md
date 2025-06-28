# Developer Primer

## Как использовать Memory Bank

- Все ключевые решения фиксируйте в decisionLog.md с датой, автором и обоснованием.
- Для новых участников — начните с projectBrief.md и productContext.md.
- Используйте systemPatterns.md для описания повторяющихся архитектурных решений.
- В каждом режиме (Architect, Code, Ask, Debug) следуйте YAML-конфигу в custom_modes/.
- Для интеграции с AI-ассистентами используйте REST/MCP endpoint для автоматического логирования событий.
- Пример заполнения — см. knowledge_packages/*.md 

## Синхронизация с MCP/Task Tracker

> **Важно:** Memory Bank не предназначен для ручного ведения задач, багов или улучшений. Все подобные события фиксируются только в MCP/Task Tracker, а Memory Bank служит журналом и контекстным отражением для AI, автоматизации и команды.

### Рекомендации
- Создавайте и обновляйте задачи только через MCP (API, UI, CLI).
- Memory Bank автоматически отражает события, статусы и решения из MCP.
- ACT (AI Context Tracker) отслеживает действия в MCP и обновляет Memory Bank.
- Не добавляйте задачи напрямую в Memory Bank.

### Пример workflow
1. Задача создаётся в MCP.
2. MCP обновляет статус и отправляет событие в Memory Bank.
3. ACT логирует действия и обновляет контекст.
4. Баги/улучшения фиксируются только в MCP, а Memory Bank отражает эти события. 

### Чеклист: Проверка подключения к MCP/Task Tracker

- [ ] Выполнен healthcheck MCP API (`/health`)
- [ ] Получен валидный ответ и статус "OK"
- [ ] Тестовая задача из MCP появилась в Memory Bank
- [ ] Логи интеграции фиксируют успешную синхронизацию
- [ ] В интерфейсе Memory Bank отображается статус подключения

#### Инструкция
1. Проверьте, что MCP API доступен по адресу `/health` и возвращает статус `ok`.
2. Создайте тестовую задачу через MCP (UI/API).
3. Убедитесь, что задача автоматически отражается в Memory Bank (`decisionLog.md`, `activeContext.md`).
4. Проверьте логи интеграции (например, `integrationLog.md` или system log).
5. В UI/CLI Memory Bank должен отображаться статус подключения к MCP.

#### Пример Python-скрипта для healthcheck
```python
import requests

def check_mcp_connection(mcp_url, token):
    try:
        resp = requests.get(f'{mcp_url}/health', headers={'Authorization': f'Bearer {token}'})
        if resp.status_code == 200 and resp.json().get('status') == 'ok':
            print('MCP подключён')
            return True
        else:
            print('Ошибка подключения к MCP:', resp.text)
            return False
    except Exception as e:
        print('Ошибка:', e)
        return False
``` 

### Лог-файл интеграции
Ведите integrationLog.md для всех попыток синхронизации с MCP (см. шаблон).

### Автотесты интеграции
- Реализуйте регулярные тесты доступности MCP, корректности синхронизации и актуальности данных.
- Пример теста:
```python
# test_mcp_integration.py
assert check_mcp_connection(mcp_url, token)
```

### UI/CLI-индикатор статуса
- В интерфейсе Memory Bank отображайте статус подключения к MCP.
- CLI-команда: `memory-bank check-mcp-connection`

### Автоматические уведомления о сбоях
- Настройте оповещения (Slack, email, Sentry) при ошибках интеграции.
- Пример: при 3 неудачных попытках sync — уведомить DevOps.

### Документация по ошибкам и FAQ
- Разделите типовые ошибки (401, 500, timeout) и способы их устранения.