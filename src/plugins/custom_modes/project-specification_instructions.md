# PROJECT SPECIFICATION MODE (Расширенный шаблон)

Этот режим предназначен для поэтапного, командного и AI-ассистируемого создания проектной документации с максимальной детализацией, автоматизацией, поддержкой federation и best practices.

---

# Project Brief: <Название проекта>

## 1. Мета-данные
- Project ID: <...>
- Владелец: <...>
- Дата старта: <...>
- Версия: <...>
- Статус: draft
- Ссылки: <...>

## 2. Stakeholders & Roles
| Имя | Роль | Ответственность | Контакт |
|-----|------|----------------|---------|
|     |      |                |         |

## 3. Product Strategy & Vision
- Миссия: <...>
- Ценности: <...>
- SWOT: <...>
- Feature matrix: <...>

## 4. Customer Segmentation & Personas
- Сегменты: B2B/B2C, SMB/Enterprise, отрасли, география, возраст, доход, digital-уровень
- Персоны: цели, боли, сценарии, триггеры покупки, возражения, каналы коммуникации
- AI-анализ: автоматическая кластеризация клиентов по данным/опросам

## 5. Customer Intelligence & Deep Insights
- Портреты клиентов: демография, психографика (ценности, стиль жизни, digital-уровень, привычки, любимые бренды)
- Customer Stories: реальные истории, интервью, цитаты, "день из жизни клиента"
- AI-анализ отзывов/форумов: автоматический сбор и кластеризация боли/ожиданий
- Customer Success Map: что для клиента "успех", как он измеряет value

## 4. User Research & Personas
- Персоны: цели, боли, сценарии, цитаты
- AI-генерация гипотез, pain points из отзывов

## 5. Customer Journey & Experience Map
- Для каждого сегмента: путь, эмоции, pain points, точки контакта
- Визуализация: Mermaid/PlantUML

## 6. Problem Space & Opportunity Mapping
- 100+ проблем, категории, impact/urgency
- Opportunity backlog (AI)

## 7. Solution Space
- Функциональные требования, user stories, acceptance criteria
- AI-генерация альтернатив, trade-off analysis

## 8. Roadmap & Release Plan
- Gantt, story map, value/effort matrix, критические пути
- AI-автоматизация roadmap, выявление bottlenecks

## 9. Architecture & Integrations
- Архитектурные схемы (UML, C4, sequence, deployment)
- Интеграции, API, внешние сервисы, AI-оценка рисков

## 10. Analytics & Success Metrics
- KPI/OKR, продуктовые метрики, события аналитики (GA4, BI)
- AI-генерация дашбордов, автоматизация сбора метрик

## 11. Security & Compliance
- Требования по безопасности, GDPR, регуляции
- AI-чеклист: шифрование, аутентификация, аудит, backup

## 12. UX/UI & Accessibility
- Гайдлайны, дизайн-система, accessibility (WCAG), AI-ревью макетов
- Визуализация: moodboard, UI-kit

## 13. Delivery & Estimation
- Таблица: задачи, story points, роли, дедлайны, зависимости
- AI-оценка рисков по срокам, автоматизация перепланирования

## 14. Risks & Mitigation
- Категории: бизнес, технические, продуктовые, внешние
- AI-генерация mitigation-планов, мониторинг рисков

## 15. Acceptance Criteria & Definition of Done
- Для каждой фичи/релиза: критерии, тест-кейсы, AI-checklist

## 16. Change Log & Decision Log
- История изменений, ключевые решения, AI-логирование

## 17. Federation & Knowledge Sharing
- Экспорт/импорт спецификации, шаблонов, best practices между проектами/инстансами

---

## AI-автоматизация и ревью
- AI-ревью: автоматическая проверка полноты, связности, актуальности, выявление дубликатов, устаревших требований
- AI-генерация вопросов для уточнения по каждому разделу
- AI-инициатор: предлагает создать снапшот, провести ревью, экспортировать спецификацию
- AI-логирование: все действия фиксируются в auditLog.md, changelog, decisionLog.md

---

## Формат и экспорт
- Все документы — markdown, с оглавлением, ссылками, визуализациями (Mermaid, PlantUML)
- Возможность экспорта в PDF, Confluence, Notion, federation-архив
- Для каждого раздела — AI-комментарии и рекомендации (выделять как > AI: ...)

---

## Примеры CLI/AI-запросов
- `ai-assistant generate-spec --type landing --audience freelancers,managers --problems 100`
- `ai-assistant review-spec --file projectBrief.md`
- `ai-assistant export-spec --to federation`
- `ai-assistant roadmap --out roadmap.mmd`
- `ai-assistant audit-risks --file projectBrief.md`

---

## Чек-лист полноты (AI-автоматизация)
- [ ] Все роли и стейкхолдеры описаны
- [ ] Персоны и сегменты с pain points
- [ ] 100+ проблем, opportunity backlog
- [ ] Customer Journey с визуализацией
- [ ] Roadmap, story map, value/effort matrix
- [ ] Архитектура, интеграции, sequence diagrams
- [ ] Метрики, события аналитики, BI
- [ ] Security, compliance, DRP
- [ ] Дизайн-система, accessibility
- [ ] Оценка трудозатрат, зависимости
- [ ] Риски и mitigation-планы
- [ ] Критерии приёмки, тест-кейсы
- [ ] История изменений, решения
- [ ] Federation-ready (экспорт/импорт)
- [ ] Документ прошёл AI-ревью

---

## Best practices
- Использовать AI для генерации, ревью, автоматизации
- Все ключевые решения и изменения логировать
- Визуализировать сложные процессы (Mermaid/UML)
- Связывать спецификацию с core-файлами Memory Bank
- Регулярно экспортировать/импортировать спецификации для обмена знаниями

---

## Инструкции для AI
- Анализируй запрос, определяй тип проекта, выделяй ключевые элементы (аудитория, проблемы, каналы)
- Сегментируй аудиторию (3–6 групп), указывай характеристики, задачи, мотивы
- Собирай 100+ проблем, связывай с сегментами и функциями, оценивай вероятность
- Описывай Customer Journeys для каждого сегмента, указывай каналы
- Детализируй каналы продаж, оценивай CAC, ROI, приоритет
- Создавай функционал, связывай с проблемами
- Добавляй UML/диаграммы для процессов/архитектуры
- Оценивай трудозатраты, формируй таблицу
- Указывай риски и критерии, формируй mitigation-план
- Форматируй в markdown, включай визуализации, AI-комментарии
- После генерации — инициируй AI-ревью, экспорт, снапшот

---

## Пример projectBrief.md (структура)
# Project Brief: <Название проекта>

## 1. Мета-данные
- Project ID: <...>
- Владелец: <...>
- Дата старта: <...>
- Версия: <...>
- Статус: <...>
- Ссылки: <...>

## 2. Stakeholders & Roles
| Имя | Роль | Ответственность | Контакт |
|-----|------|----------------|---------|
|     |      |                |         |

## 3. Product Strategy & Vision
- Миссия: <...>
- Ценности: <...>
- SWOT: <...>
- Feature matrix: <...>

## 4. User Research & Personas
- Персоны: <...>
- Pain points: <...>

## 5. Customer Journey & Experience Map
- Для каждого сегмента: <...>
- Визуализация: <Mermaid/UML>

## 6. Problem Space & Opportunity Mapping
- Категории проблем: <...>
- Opportunity backlog: <...>

## 7. Solution Space
- User stories: <...>
- Acceptance criteria: <...>
- Альтернативы: <...>

## 8. Roadmap & Release Plan
- Gantt/story map: <...>
- Value/effort matrix: <...>

## 9. Architecture & Integrations
- Архитектура: <...>
- Интеграции: <...>
- Sequence diagrams: <...>

## 10. Analytics & Success Metrics
- KPI/OKR: <...>
- Метрики: <...>
- BI/дашборды: <...>

## 11. Security & Compliance
- Требования: <...>
- DRP: <...>

## 12. UX/UI & Accessibility
- Дизайн-система: <...>
- Accessibility: <...>

## 13. Delivery & Estimation
- Таблица: <...>
- Story points: <...>

## 14. Risks & Mitigation
- Риски: <...>
- Mitigation: <...>

## 15. Acceptance Criteria & DoD
- Критерии: <...>
- Тест-кейсы: <...>

## 16. Change Log & Decision Log
- История изменений: <...>
- Ключевые решения: <...>

## 17. Federation & Knowledge Sharing
- Экспорт/импорт: <...>

## 18. Чек-лист полноты
- [ ] ...

> AI: Все разделы автоматически проверяются на полноту, связность, актуальность. После генерации — инициировать AI-ревью, экспорт, снапшот.

## 30. Hypotheses (Гипотезы)
| Сегмент | Гипотеза | Критерий проверки | Результат теста |
|---------|----------|-------------------|-----------------|
|         |          |                   |                 |

## 31. Market Sizing (TAM/SAM/SOM)
- TAM: <...>
- SAM: <...>
- SOM: <...>
- Источники данных: <...>
- Методика расчёта: <...>
- Целевая доля рынка: <...>
- График динамики рынка: <...>

## 32. Competitors & Killer Features
| Конкурент | Killer features | Причины выбора | Сегменты | Цена |
|-----------|----------------|---------------|----------|------|
|           |                |               |          |      |
- SWOT-конкурентов: <...>
- AI-анализ отзывов конкурентов: <...>
- Customer switching triggers: <...>

## 33. Customer Willingness to Pay
- Опросы: <...>
- A/B тесты: <...>
- Сегментация по доходу: <...>
- Платежные барьеры: <...>
- AI-анализ транзакций: <...>

## 34. Channels & Acquisition
- Карта каналов: <...>
- Эффективность (CAC, LTV): <...>
- Growth loops: <...>
- Customer journey по каналам: <...>
- AI-анализ каналов: <...>

# ... AI-комментарий ...

## 35. Customer Validation & Evidence
- Документированные интервью: <...>
- AI-анализ customer feedback: <...>
- Customer advisory board: <...>
- LOI (письма о намерениях): <...>

## 36. Go-to-Market (GTM) & Launch Readiness
- GTM checklist: <...>
- План коммуникаций: <...>
- AI-анализ рисков запуска: <...>

## 37. Retention & Expansion
- Cohort analysis: <...>
- Expansion revenue: <...>
- AI-прогноз churn/retention: <...>

## 38. Product Analytics & Experimentation
- Система экспериментов: <...>
- AI-генерация новых экспериментов: <...>
- Feature adoption metrics: <...>

## 39. Regulatory & Compliance Deep Dive
- Карта регуляторных требований по регионам: <...>
- AI-мониторинг изменений в законах: <...>

## 40. Sustainability & Social Impact (расширено)
- Carbon footprint: <...>
- DEI (Diversity, Equity, Inclusion): <...>
- AI-анализ социальных трендов: <...>

## 41. AI/ML Strategy (углубить)
- AI explainability: <...>
- AI governance: <...>
- AI roadmap: <...>

## 42. Ecosystem Mapping (визуализация)
- Mermaid/Graphviz карта экосистемы: <...>
- AI-анализ влияния экосистемы: <...>

## 43. Knowledge Management
- AI-автоматизация поиска знаний: <...>
- Lessons learned: <...>

## 44. AI-Driven Alerts & Monitoring
- AI-алерты по ключевым метрикам: <...>
- AI-инициатор действий: <...>

# ... AI-комментарий ...

## 45. Product Localization & Internationalization
- Локализация интерфейса: <...>
- Адаптация под локальные рынки: <...>
- AI-анализ культурных особенностей: <...>

## 46. Customer Support & Success
- Система поддержки: <...>
- Customer success процессы: <...>
- AI-анализ обращений: <...>

## 47. Brand & Positioning
- Позиционирование на рынке: <...>
- Brand attributes: <...>
- AI-анализ восприятия бренда: <...>

## 48. Pricing Experiments & Elasticity
- Эксперименты с ценами: <...>
- Ценовая эластичность: <...>
- AI-прогноз реакции на изменение цен: <...>

## 49. Partnerships & Alliances
- Ключевые партнёры: <...>
- Стратегические альянсы: <...>
- AI-поиск новых партнёров: <...>

## 50. Intellectual Property & Patents
- Патенты: <...>
- Торговые марки: <...>
- AI-мониторинг нарушений: <...>

# ... AI-комментарий ...

## 51. Problem Clustering & Graph Analysis
- Граф проблем и сегментов (Mermaid/Graphviz):
  ```mermaid
  graph TD
    B2B --> HighCost
    B2C --> LowTrust
    B2B --> IntegrationPain
    B2C --> UXIssues
    HighCost --> PriceOptimizer
    IntegrationPain --> APIv2
  ```
- AI-кластеризация проблем:
  - Кластер 1: "Стоимость" — HighCost, ExpensiveOnboarding, HiddenFees
  - Кластер 2: "UX" — UXIssues, ComplicatedFlow, SlowSupport
  - Кластер 3: "Интеграции" — IntegrationPain, NoZapier, APIv1Bugs
- Матрица "problem x segment":
  | Проблема         | B2B | B2C | SMB | Enterprise |
  |------------------|-----|-----|-----|------------|
  | HighCost         |  X  |     |  X  |     X      |
  | UXIssues         |     |  X  |  X  |            |
  | IntegrationPain  |  X  |     |     |     X      |
- Heatmap проблем по сегментам: (AI может сгенерировать цветовую карту — чем темнее, тем чаще встречается проблема)

## 52. Problem Distribution (Bell Curve)
- Bell curve проблем (гистограмма/кривая):
  - Ядро: HighCost (30%), UXIssues (25%), IntegrationPain (20%)
  - Длинный хвост: RareBug1 (1%), RareBug2 (0.5%), ...
- Таблица фокусных проблем:
  | Проблема        | Частота | Сегменты   | Фичи         | Impact |
  |-----------------|---------|------------|--------------|--------|
  | HighCost        | 30%     | B2B, SMB   | PriceOpt     | High   |
  | UXIssues        | 25%     | B2C, SMB   | UIv2         | High   |
  | IntegrationPain | 20%     | B2B, Ent.  | APIv2        | High   |
- AI-рекомендация по фокусу:
  > AI: Рекомендуется сфокусироваться на HighCost и UXIssues — они покрывают 55% всех болей и влияют на ключевые сегменты.

## 53. Advanced Competitor Analysis
- Список конкурентов:
  | Название   | Сайт           | Сегменты | Killer features   | Цена | Причины выбора      |
  |------------|----------------|----------|------------------|------|---------------------|
  | CompA      | compa.com      | B2B      | FastAPI, Support | $$$  | Скорость, API       |
  | CompB      | compb.com      | B2C      | UX, Mobile       | $$   | Удобство, мобильность|
  | CompC      | compc.com      | SMB      | Price, Integr.   | $    | Цена, интеграции    |
- SWOT-конкурентов:
  - Сильные стороны: быстрый API, сильная поддержка, UX
  - Слабые стороны: высокая цена, мало интеграций
  - Возможности: новые рынки, AI-фичи
  - Угрозы: демпинг, новые игроки
- AI-анализ отзывов конкурентов:
  - Что хвалят: "Очень быстрый API", "Отличная поддержка"
  - Что ругают: "Дорого", "Сложно интегрировать"
  - Unmet needs: "Нет Zapier", "Нет мобильного приложения"
- Визуализация конкурентного поля (Mermaid/heatmap):
  ```mermaid
  graph LR
    CompA -- FastAPI --> B2B
    CompB -- UX --> B2C
    CompC -- Price --> SMB
    OurProduct -- UniqueAI --> B2B
  ```

> AI: Для автоматизации кластеризации, построения графов и анализа конкурентов используйте embedding/semantic similarity, парсинг отзывов, автоматическую генерацию heatmap и bell curve. AI может рекомендовать фокусные проблемы и выявлять "дыры" на рынке.