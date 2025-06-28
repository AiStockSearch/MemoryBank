# QA MODE (Режим тестировщика)

QA MODE предназначен для автоматизации и управления качеством, с акцентом на интеграционное тестирование, генерацию тест-кейсов, интеграцию с CI/CD и публикацию отчётов.

## Workflow интеграционного тестирования
1. AI-генерация интеграционных тест-кейсов по спецификациям, user stories, acceptance criteria.
2. Выбор и настройка инструментов: Maestro Dev (mobile), Cypress (web), ПК-интеграция (desktop, API).
3. Автоматизация запуска тестов в CI/CD (GitHub Actions, Jenkins, GitLab CI).
4. Сбор и публикация отчётов (Allure, JUnit, custom dashboards).
5. Peer review: AI-генерация вопросов, автоматизация сбора обратной связи.
6. AI-генерация action items по итогам тестирования.
7. Мониторинг и алерты: автоматизация отслеживания падений, алертов в Slack/Teams.

## AI-генерация интеграционных тест-кейсов
- AI автоматически формирует тест-кейсы по user stories, acceptance criteria, спецификациям API.
- Пример: "AI сгенерировал тест-кейс: 'Проверить интеграцию Maestro Dev с push-уведомлениями'."

## Maestro Dev (mobile)
- Шаблоны для интеграционных тестов мобильных приложений (Android/iOS) с Maestro Dev.
- Пример:
```yaml
# Maestro Dev: тест push-уведомлений
appId: com.example.app
flow:
  - launchApp
  - tapOn: 'Войти'
  - assertVisible: 'Главная'
```

## Cypress (web)
- Шаблоны для интеграционных тестов web-интерфейсов с Cypress.
- Пример:
```js
// Cypress: тест интеграции с API
cy.request('/api/login').then((resp) => {
  expect(resp.status).to.eq(200)
})
```

## ПК-интеграция (desktop/API)
- Шаблоны для интеграционных тестов desktop-приложений, API, микросервисов.
- Пример:
```python
# Pytest: интеграционный тест API
import requests
resp = requests.post('http://localhost:8000/api/login', json={...})
assert resp.status_code == 200
```

## Интеграция с CI/CD
- Автоматизация запуска тестов при pull request, публикация статусов, отчётов (GitHub Actions, Jenkins, GitLab CI).
- Пример:
```yaml
# GitHub Actions: запуск Cypress
- name: Run Cypress tests
  run: npx cypress run
```

## Публикация отчётов
- Автоматизация публикации отчётов (Allure, JUnit, custom dashboards), интеграция с корпоративными порталами.
- Пример: "Отчёт Allure опубликован, ссылка добавлена в Confluence."

## Peer review и action items
- AI-генерация вопросов для peer review, автоматизация сбора обратной связи, формирование action items.
- Пример: "Peer review: добавить тест на интеграцию с Maestro Dev."

## Мониторинг и алерты
- Автоматизация мониторинга падений тестов, алертов в Slack/Teams, публикация статусов.
- Пример: "Алерт: интеграционный тест Cypress упал — уведомление отправлено в #qa."

## Расширенный чек-лист
- [ ] Интеграционные тест-кейсы сгенерированы AI
- [ ] Maestro Dev тесты реализованы
- [ ] Cypress тесты реализованы
- [ ] ПК-интеграция покрыта тестами
- [ ] CI/CD автоматизирован
- [ ] Отчёты опубликованы
- [ ] Peer review проведён
- [ ] Action items зафиксированы
- [ ] Мониторинг/алерты настроены

## Пример peer review
- "Добавить тест на интеграцию с Maestro Dev."
- "Покрыть edge-case для Cypress."

## E2E (End-to-End) тесты
- Проверяют работу всей цепочки микросервисов и бизнес-процессов "от пользователя до БД".
- Инструменты: Cypress, Playwright, Selenium, TestCafe, REST-assured, Supertest.
- Пример:
```js
// Playwright: E2E тест авторизации
await page.goto('https://app.example.com/login');
await page.fill('#email', 'user@example.com');
await page.fill('#password', 'password');
await page.click('button[type=submit]');
await expect(page).toHaveURL('https://app.example.com/dashboard');
```
- Автоматизация запуска в CI/CD, публикация отчётов (Allure, custom dashboards).

## Тесты устойчивости (Resilience/Chaos Testing)
- Проверяют поведение системы при сбоях, отказах сервисов, задержках, потере соединения.
- Инструменты: Chaos Monkey, Gremlin, Toxiproxy, Pumba.
- Пример:
```bash
# Gremlin: отключить сервис payments на 60 сек
$ gremlin attack shutdown --target payments --length 60
```
- Автоматизация запуска сценариев хаоса, публикация отчётов, алертов в Slack/Teams.

## Performance/Load/Stress тесты
- Проверяют производительность, масштабируемость, поведение под нагрузкой.
- Инструменты: Locust, k6, JMeter, Artillery.
- Пример:
```python
# Locust: нагрузочный тест login
from locust import HttpUser, task
class WebsiteUser(HttpUser):
    @task
def login(self):
        self.client.post('/api/login', json={...})
```
- Автоматизация запуска в CI/CD, публикация метрик, алертов при деградации.

## Security Testing
- Проверяют уязвимости, неправильные настройки, XSS, SQLi, CSRF, открытые порты, права.
- Инструменты: OWASP ZAP, Snyk, Trivy, Nikto, Burp Suite.
- Пример:
```bash
# OWASP ZAP: сканирование API
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:8000/api
```
- Автоматизация сканирования в CI/CD, публикация отчётов, алертов о найденных уязвимостях.

## Data Consistency/Replication Tests
- Проверяют целостность и согласованность данных между сервисами, репликацию, eventual consistency.
- Инструменты: custom scripts (Python, SQL), Debezium, Kafka Connect, CDC tools.
- Пример:
```python
# Проверка согласованности данных между сервисами
users_a = get_users_from_service_a()
users_b = get_users_from_service_b()
assert set(users_a) == set(users_b)
```
- Автоматизация запуска тестов, публикация отчётов о расхождениях, алертов при нарушении консистентности.

## Контрактные тесты (Contract Testing)
- Проверяют, что взаимодействие между сервисами соответствует согласованному API/контракту.
- Инструменты: Pact, Spring Cloud Contract, Dredd, Hoverfly.
- Пример:
```js
// Pact: контрактный тест для API
const { Pact } = require('@pact-foundation/pact');
// ...описание provider/consumer, взаимодействий...
```
- Автоматизация проверки контрактов в CI/CD, публикация отчётов о несовместимостях.

## Smoke/Sanity тесты
- Быстрые проверки "жизни" основных функций после деплоя.
- Инструменты: custom scripts, Postman, REST-assured.
- Пример:
```bash
# Smoke test: проверка доступности сервисов
curl -f http://service-a/health || exit 1
curl -f http://service-b/health || exit 1
```
- Автоматизация запуска после деплоя, алерты при сбоях.

## Тесты очередей/асинхронных взаимодействий
- Проверяют корректность работы с брокерами сообщений (Kafka, RabbitMQ), обработку событий, idempotency.
- Инструменты: Testcontainers, custom scripts, kafkacat.
- Пример:
```python
# Проверка доставки сообщений в Kafka
from kafka import KafkaProducer, KafkaConsumer
producer.send('topic', b'message')
msg = next(consumer)
assert msg.value == b'message'
```
- Автоматизация тестов в CI/CD, публикация отчётов о потерянных/дублированных сообщениях.

## Мультиязычное тестирование
- Проверяют корректность локализации, отображения переводов, RTL-режимов.
- Инструменты: Cypress, Playwright, custom scripts.
- Пример:
```js
// Cypress: тест локализации
cy.visit('/?lang=ar')
cy.contains('تسجيل الدخول') // Проверка RTL
```
- Автоматизация проверки переводов, публикация отчётов о пропущенных ключах.

## Интеграция с Sentry
- Проверяют корректность интеграции с Sentry, автоматизацию алертов по ошибкам.
- Инструменты: Sentry SDK, custom scripts.
- Пример:
```python
# Проверка отправки ошибок в Sentry
import sentry_sdk
try:
    1/0
except Exception as e:
    sentry_sdk.capture_exception(e)
```
- Автоматизация проверки алертов, публикация отчётов о необработанных ошибках.

## Генерация моков
- Автоматизация генерации моков для внешних сервисов, API, очередей.
- Инструменты: WireMock, MockServer, Hoverfly, custom scripts.
- Пример:
```js
// WireMock: мок для внешнего API
wiremock.stubFor(get(urlEqualTo('/api/external')).willReturn(aResponse().withStatus(200)))
```
- Автоматизация запуска моков в тестовой среде, публикация статусов. 