# PROJECT SPECIFICATION MODE (Расширенный мод создания проектной документации)

Этот режим предназначен для поэтапного, командного и AI-ассистируемого создания проектной документации с максимальной детализацией, автоматизацией, поддержкой federation и best practices.

---

## 1. Мета-данные проекта
- Project ID, владелец, дата старта, версия, статус (draft, review, approved, archived)
- Ссылки: репозиторий, таск-трекер, Figma, Confluence, Memory Bank, снапшоты

## 2. Stakeholders & Roles
- Таблица: имя, роль, зона ответственности, контакт
- AI-генерация вопросов для каждого стейкхолдера

## 3. Product Strategy & Vision
- Миссия, ценностное предложение, дифференциаторы
- SWOT, feature matrix, анализ конкурентов (AI)

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