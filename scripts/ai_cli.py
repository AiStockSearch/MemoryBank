import argparse
import sys
import os
from scripts.ai_utils import generate_task_summary, analyze_task_links, generate_mermaid_diagram, review_changelog, generate_roadmap
from scripts.ai_assistant import get_tasks

def cmd_summary(args):
    tasks = get_tasks()
    if args.task_id:
        task = next((t for t in tasks if t['id'] == args.task_id), None)
        if not task:
            print(f"Задача с id {args.task_id} не найдена.")
            sys.exit(1)
        summary = generate_task_summary(task)
        print(summary)
    else:
        for task in tasks:
            print(generate_task_summary(task))
            print("-"*40)

def cmd_links(args):
    tasks = get_tasks()
    missing = analyze_task_links(tasks)
    if missing:
        print(f"Задачи без связей с epic/business_goal: {missing}")
    else:
        print("Все задачи связаны с epic и бизнес-целями.")

def cmd_diagram(args):
    tasks = get_tasks()
    if args.type == "task_links":
        data = [(t['id'], t.get('epic','-'), t.get('business_goal','-')) for t in tasks]
        out_path = args.out or "task_links.mmd"
        generate_mermaid_diagram("task_links", data, out_path)
        print(f"Диаграмма связей задач сохранена в {out_path}")
    elif args.type == "task_lifecycle":
        out_path = args.out or "task_lifecycle.mmd"
        generate_mermaid_diagram("task_lifecycle", None, out_path)
        print(f"Диаграмма жизненного цикла сохранена в {out_path}")
    else:
        print("Неизвестный тип диаграммы. Используйте task_links или task_lifecycle.")
        sys.exit(1)

def cmd_review_changelog(args):
    summary, recommendations = review_changelog(args.changelog)
    print("=== AI-ревью CHANGELOG ===")
    print(summary)
    print("--- Рекомендации ---")
    print(recommendations)

def cmd_roadmap(args):
    tasks = get_tasks()
    stages = generate_roadmap(tasks)
    out_path = args.out or "roadmap.mmd"
    generate_mermaid_diagram("roadmap", stages, out_path)
    print(f"Gantt-диаграмма roadmap сохранена в {out_path}")

def cmd_generate_spec(args):
    # Генерация projectBrief.md по расширенному шаблону
    project_type = args.type or 'landing'
    audience = args.audience.split(',') if args.audience else ['freelancers', 'managers']
    problems_count = int(args.problems) if args.problems else 100
    project_name = args.name or 'Demo Project'
    out_path = args.out or 'projectBrief.md'

    # Скелет расширенного шаблона (можно вынести в отдельный файл)
    content = f"""# Project Brief: {project_name}

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

## 4. User Research & Personas
- Персоны: {', '.join(audience)}
- Pain points: <...>

## 5. Customer Journey & Experience Map
- Для каждого сегмента: <...>
- Визуализация: <Mermaid/UML>

## 6. Problem Space & Opportunity Mapping
- Категории проблем: <...>
- Opportunity backlog: <...>
- Пример проблем:
"""
    for i in range(1, problems_count+1):
        content += f"- Проблема {i}: <описание>\n"
    content += """

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
"""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'projectBrief.md сгенерирован по расширенному шаблону: {out_path}')

def main():
    parser = argparse.ArgumentParser(description="AI-ассистент CLI: summary, links, diagram, review-changelog, roadmap, generate-spec")
    subparsers = parser.add_subparsers(dest="command")

    p_summary = subparsers.add_parser("summary", help="Сгенерировать summary по задаче или всем задачам")
    p_summary.add_argument("--task-id", help="ID задачи (если не указано — по всем)")
    p_summary.set_defaults(func=cmd_summary)

    p_links = subparsers.add_parser("links", help="Проверить связи задач с epic и бизнес-целями")
    p_links.set_defaults(func=cmd_links)

    p_diagram = subparsers.add_parser("diagram", help="Сгенерировать mermaid-диаграмму связей или жизненного цикла")
    p_diagram.add_argument("--type", required=True, help="Тип диаграммы: task_links или task_lifecycle")
    p_diagram.add_argument("--out", help="Путь для сохранения диаграммы")
    p_diagram.set_defaults(func=cmd_diagram)

    p_review = subparsers.add_parser("review-changelog", help="AI-ревью CHANGELOG.md: анализ, рекомендации")
    p_review.add_argument("--changelog", default="CHANGELOG.md", help="Путь к changelog (по умолчанию CHANGELOG.md)")
    p_review.set_defaults(func=cmd_review_changelog)

    p_roadmap = subparsers.add_parser("roadmap", help="Сгенерировать Gantt-диаграмму roadmap по задачам")
    p_roadmap.add_argument("--out", help="Путь для сохранения диаграммы")
    p_roadmap.set_defaults(func=cmd_roadmap)

    p_generate = subparsers.add_parser("generate-spec", help="Сгенерировать projectBrief.md по расширенному шаблону")
    p_generate.add_argument("--type", help="Тип проекта (landing, app, saas и т.д.)")
    p_generate.add_argument("--audience", help="Сегменты аудитории через запятую")
    p_generate.add_argument("--problems", help="Количество проблем (по умолчанию 100)")
    p_generate.add_argument("--name", help="Название проекта")
    p_generate.add_argument("--out", help="Путь для сохранения projectBrief.md")
    p_generate.set_defaults(func=cmd_generate_spec)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 