# Workflow и автоматизация

## Mermaid-схема жизненного цикла задачи

```mermaid
flowchart TD
    BZ[Бизнесовая задача<br/>(business-tasks.md)] -->|Декомпозиция| PLAN[Планирование<br/>(plan-tasks.md)]
    PLAN -->|Если нужен креатив| CREATIVE[Креатив<br/>(creative-tasks.md)]
    CREATIVE --> PLAN
    PLAN -->|Готово к реализации| IMPLEMENT[Реализация<br/>(implement-tasks.md)]
    IMPLEMENT --> REFLECT[Ретроспектива/Архив<br/>(reflection-tasks.md)]
    REFLECT -->|Новые инсайты| PLAN
    PLAN -->|Если не нужен креатив| IMPLEMENT
    BZ -->|Иногда напрямую| PLAN
```

## Статусы задач
- Plan: задача на этапе планирования
- Creative: требуется креатив/альтернатива
- Implement: задача в реализации
- Done: задача завершена
- Reflection: анализ и ретроспектива

## Рекомендации по автоматизации
- Используйте скрипт generate_memory_bank.py для создания структуры и шаблонов
- Для каждой новой фичи используйте --create-feature
- Проверяйте связи между бизнесовыми и техническими задачами (см. business-tasks.md)
- Внедряйте автоматическую валидацию связей через CI/CD или AI-ассистента 