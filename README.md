# Эпик 4: GraphQL (Обновлено)

## Описание

Эпик реализует GraphQL API для гибкого доступа к данным, задачам и federation. Обновление включает улучшения из `mcp_improvements.md`: запросы для предзаполнения, подписки для real-time предпросмотра, оптимизацию для массовых операций, уведомления с аналитикой и UI интеграцию с Cursor IDE.

**Ожидаемый результат**:
- GraphQL-схема для задач, правил, знаний, событий.
- Подписки для real-time обновлений и предпросмотра.
- Поддержка массовых операций (1000+ записей).
- Уведомления через Telegram, macOS, Apple Push, Slack, email с аналитикой.
- Интеграция с UI Cursor IDE для предпросмотра.

**Зависимости**: Эпик 6 (Security).  
**Приоритет**: P2  
**Оцениваемая длительность**: 10 дней.

---

## Пул задач

### Задача 1: Создание GraphQL-схемы
- **Описание**: Определить схему для данных.
- **Подзадачи**:
  - Использовать `ariadne` для схемы.
  - Определить типы: `Task`, `Rule`, `Knowledge`, `Log`.
  - Добавить тип `Autofill` для предзаполнения.
  - Проверить валидность схемы.
- **Длительность**: 1.5 дня.
- **Ответственный**: Backend Developer.

### Задача 2: Реализация запросов
- **Описание**: Реализовать запросы для получения данных.
- **Подзадачи**:
  - Добавить `Query` для `tasks`, `rules`, `logs`.
  - Подключить к `archive/` и `memory-bank/`.
  - Оптимизировать для массовых операций.
  - Добавить запрос `autofillTask` для предзаполнения.
- **Длительность**: 1.5 дня.
- **Ответственный**: Backend Developer.

### Задача 3: Реализация мутаций
- **Описание**: Реализовать мутации для изменения данных.
- **Подзадачи**:
  - Добавить `Mutation` для создания/обновления задач, правил.
  - Валидировать входные данные.
  - Логировать в `auditLog.md`.
  - Добавить мутацию `autofillTask` для предзаполнения.
- **Длительность**: 1.5 дня.
- **Ответственный**: Backend Developer.

### Задача 4: Подписки
- **Описание**: Настроить real-time подписки.
- **Подзадачи**:
  - Реализовать `Subscription` с WebSocket.
  - Отправлять события при обновлениях.
  - Добавить подписку для предпросмотра изменений.
  - Оптимизировать для массовых операций.
- **Длительность**: 1.5 дня.
- **Ответственный**: Backend Developer.

### Задача 5: Ограничение доступа
- **Описание**: Ограничить мутации и подписки по ролям.
- **Подзадачи**:
  - Интегрировать с JWT-авторизацией.
  - Определить роли (`admin`, `user`).
  - Добавить авторизацию для предзаполнения.
  - Проверить ограничения.
- **Длительность**: 1 день.
- **Ответственный**: Backend Developer.

### Задача 6: Расширенные уведомления
- **Описание**: Интегрировать уведомления с GraphQL.
- **Подзадачи**:
  - Отправлять уведомления через `src/notifications.py`.
  - Поддержать Telegram, macOS, Apple Push, Slack, email.
  - Добавить аналитику (время, объем).
  - Реализовать группировку.
- **Длительность**: 1.5 дня.
- **Ответственный**: Backend Developer.

### Задача 7: Улучшение плагина Cursor IDE
- **Описание**: Добавить UI и автодополнение.
- **Подзадачи**:
  - Обновить `src/cursor_plugin/` с UI для предпросмотра GraphQL-данных.
  - Реализовать автодополнение для запросов/мутаций.
  - Настроить real-time подсказки через LLM.
- **Длительность**: 2 дня.
- **Ответственный**: Frontend Developer.

### Задача 8: Автотесты
- **Описание**: Создать тесты для GraphQL и улучшений.
- **Подзадачи**:
  - Написать тесты в `tests/test_graphql.py`.
  - Проверить запросы, мутации, подписки, предзаполнение.
  - Интегрировать в CI/CD.
- **Длительность**: 2 дня.
- **Ответственный**: QA Engineer.

### Задача 9: Документация
- **Описание**: Добавить описание в `docs/mcp_integration_usage.md`.
- **Подзадачи**:
  - Описать схему, запросы, мутации, подписки, предзаполнение.
  - Добавить инструкции для Apollo Client.
  - Проверить читаемость.
- **Длительность**: 1 день.
- **Ответственный**: Technical Writer.

---

## Риски

1. **Сложность схемы**:
   - **Последствия**: Ошибки в запросах.
   - **Смягчение**: Упростить схему, использовать инструменты валидации.
   - **Вероятность**: Средняя.

2. **Перегрузка подписок**:
   - **Последствия**: Задержки в real-time.
   - **Смягчение**: Ограничить клиентов, оптимизировать события.
   - **Вероятность**: Средняя.

3. **Ошибки авторизации**:
   - **Последствия**: Несанкционированный доступ.
   - **Смягчение**: Строгая проверка JWT, автотесты.
   - **Вероятность**: Низкая.

4. **Низкая производительность**:
   - **Последствия**: Медленные запросы.
   - **Смягчение**: Кэшировать данные, оптимизировать запросы.
   - **Вероятность**: Низкая.

5. **Ошибки UI в Cursor IDE**:
   - **Последствия**: Проблемы с предпросмотром.
   - **Смягчение**: Тестировать UI, логировать.
   - **Вероятность**: Высокая.

---

## Тестовые команды

1. `mcp graphql query tasks --username user1 --project proj1 --bulk`
2. `mcp graphql mutation autofill-task --username user2 --project proj2 --title "Test"`
3. `mcp graphql subscribe tasks --username user3 --project proj3 --preview`
4. `mcp graphql query rules --username user4 --project proj4 --notify slack`
5. `mcp graphql mutation create-task --username user5 --project proj5 --notify email`
6. `curl -X POST http://localhost:8000/graphql -d '{"query":"query { tasks(username: \"user6\", project: \"proj6\") { id } }"}'`
7. `curl -X POST http://localhost:8000/graphql -d '{"query":"mutation { autofillTask(username: \"user7\", project: \"proj7\", title: \"Test\") { id } }"}'`
8. `mcp graphql query logs --username user8 --project proj8`
9. `mcp graphql subscribe rules --username user9 --project proj9 --notify telegram`
10. `mcp graphql mutation update-task --username user10 --project proj10 --dry-run`
11. `mcp graphql query tasks --username user11 --project proj11 --limit 10`
12. `mcp graphql mutation create-rule --username user12 --project proj12 --preview`
13. `mcp graphql subscribe logs --username user13 --project proj13 --notify all`
14. `mcp graphql query tasks --username user14 --project proj14 --audit`
15. `mcp graphql mutation update-rule --username user15 --project proj15 --changelog`
16. `curl -X POST http://localhost:8000/graphql -d '{"query":"query { rules(username: \"user16\", project: \"proj16\") { name } }"}'`
17. `mcp graphql query tasks --username user17 --project proj17 --no-notify`
18. `mcp graphql subscribe tasks --username user18 --project proj18 --timeout 10`
19. `mcp graphql mutation create-task --username user19 --project proj19 --retry 3`
20. `mcp graphql query rules --username user20 --project proj20 --log-level debug`
21. `curl -X POST http://localhost:8000/graphql -d '{"query":"mutation { createTask(username: \"user21\", project: \"proj21\", data: {}) { id } }"}'`
22. `mcp graphql query tasks --username user22 --project proj22 --env prod`
23. `mcp graphql mutation autofill-task --username user23 --project proj23 --notify slack`
24. `mcp graphql subscribe rules --username user24 --project proj24 --verbose`
25. `mcp graphql query logs --username user25 --project proj25 --notify email`
26. `mcp graphql mutation update-task --username user26 --project proj26 --force`
27. `mcp graphql query tasks --username user27 --project proj27 --user-id 12345`
28. `mcp graphql subscribe logs --username user28 --project proj28 --project-id 67890`
29. `mcp graphql query rules --username user29 --project proj29 --metadata '{"key":"value"}'`
30. `mcp graphql mutation create-rule --username user30 --project proj30 --priority high`
31. `curl -X POST http://localhost:8000/graphql -d '{"query":"query { logs(username: \"user31\", project: \"proj31\") { time } }"}'`
32. `mcp graphql query tasks --username user32 --project proj32 --no-audit`
33. `mcp graphql subscribe tasks --username user33 --project proj33 --no-changelog`
34. `mcp graphql mutation autofill-task --username user34 --project proj34 --dry-run`
35. `mcp graphql query rules --username user35 --project proj35 --timeout 5`
36. `mcp graphql subscribe rules --username user36 --project proj36 --retry 5`
37. `mcp graphql query tasks --username user37 --project proj37 --notify all`
38. `mcp graphql mutation create-task --username user38 --project proj38 --log-level info`
39. `mcp graphql subscribe logs --username user39 --project proj39 --preview`
40. `mcp graphql query rules --username user40 --project proj40 --verbose`
41. `curl -X POST http://localhost:8000/graphql -d '{"query":"mutation { autofillTask(username: \"user41\", project: \"proj41\", title: \"Test\", metadata: {key: \"value\"}) { id } }"}'`
42. `mcp graphql query tasks --username user42 --project proj42 --priority low`
43. `mcp graphql mutation update-task --username user43 --project proj43 --force`
44. `mcp graphql subscribe tasks --username user44 --project proj44 --notify slack`
45. `mcp graphql query logs --username user45 --project proj45 --audit --changelog`
46. `mcp graphql mutation create-rule --username user46 --project proj46 --no-notify`
47. `mcp graphql query tasks --username user47 --project proj47 --timeout 15`
48. `mcp graphql subscribe rules --username user48 --project proj48 --retry 2`
49. `mcp graphql mutation autofill-task --username user49 --project proj49 --notify email`
50. `mcp graphql query tasks --username user50 --project proj50 --bulk --notify all`
=======
## Тестирование WebSocket и push-уведомлений

### WebSocket

1. Подключитесь к WebSocket:
   ```python
   import websockets
   import asyncio

   async def listen():
       uri = "ws://localhost:8001/ws/notify"
       async with websockets.connect(uri) as websocket:
           while True:
               msg = await websocket.recv()
               print("WS notification:", msg)

   asyncio.run(listen())
   ```