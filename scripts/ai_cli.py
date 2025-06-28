import argparse
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from ai_utils import generate_task_summary, analyze_task_links, generate_mermaid_diagram, review_changelog, generate_roadmap, ai_cluster_problems, ai_generate_graphs, ai_analyze_competitors, ai_generate_bell_curve, ai_generate_swot, ai_generate_recommendations, ai_review_spec, export_to_pdf, export_to_pptx
from ai_assistant import get_tasks
import pandas as pd

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
    # Генерация projectBrief.md по максимально расширенному шаблону
    project_type = args.type or 'landing'
    audience = args.audience.split(',') if args.audience else ['freelancers', 'managers']
    problems_count = int(args.problems) if args.problems else 100
    project_name = args.name or 'Demo Project'
    out_path = args.out or 'projectBrief.md'

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
- Сегменты: {', '.join(audience)}
- Персоны: <...>
- Психографика: <...>
- Customer Stories: <...>
- JTBD: <...>
- Триггеры/барьеры: <...>
- Customer Success Map: <...>

## 5. Customer Insights & Deep Analysis
- AI-анализ отзывов/форумов: <...>
- Кластеризация боли/ожиданий: <...>
- Цитаты клиентов: <...>

## 6. Customer Acquisition & Funnel
- Каналы: <...>
- Воронка: <...>
- CAC, CPL: <...>
- Growth loops: <...>
- Виральные механики: <...>
- Retention/engagement: <...>

## 7. Customer Value & Monetization
- Средний чек (ARPU): <...>
- LTV: <...>
- Модели монетизации: <...>
- Unit-экономика: <...>
- Payback period: <...>

## 8. Market Sizing (TAM/SAM/SOM)
- TAM: <...>
- SAM: <...>
- SOM: <...>
- Источники данных: <...>

## 9. Competitive Analysis
- Таблица конкурентов: <...>
- AI-анализ "дыр" на рынке: <...>

## 10. Pricing & Packaging
- Тарифы: <...>
- A/B тесты: <...>
- AI-рекомендации: <...>

## 11. Metrics & Analytics
- Ключевые метрики: <...>
- Динамика: <...>
- AI-прогнозы: <...>

## 12. Go-to-Market & Growth
- План запуска: <...>
- Growth experiments: <...>
- AI-идеи для роста: <...>

## 13. Financial Plan & Forecast
- P&L: <...>
- Unit-экономика: <...>
- Прогноз: <...>
- AI: Точка безубыточности, сценарии

## 14. Ecosystem & Partnerships
- Карта экосистемы: <...>
- Партнёры, интеграторы, инфлюенсеры: <...>
- API, SDK, marketplace: <...>

## 15. Team & Culture
- Командные ценности: <...>
- План развития: <...>
- AI-анализ рисков: <...>

## 16. Legal & Regulatory
- Юридические риски: <...>
- AI-мониторинг законодательства: <...>
- Force majeure: <...>

## 17. Technology & Innovation
- AI/ML roadmap: <...>
- Технологические тренды: <...>
- Open source: <...>

## 18. Sustainability & Impact
- Экологический след: <...>
- Социальная миссия: <...>
- ESG-метрики: <...>

## 19. Scenario Planning & Risk Management
- Сценарии развития: <...>
- AI-генерация "what if": <...>
- План реагирования: <...>

## 20. Continuous Discovery & Feedback
- Система сбора обратной связи: <...>
- AI-генерация гипотез: <...>
- Product discovery: <...>

## 21. Data Strategy & Privacy
- Стратегия данных: <...>
- AI-оценка рисков: <...>
- Монетизация данных: <...>

## 22. Go Global
- Мультиязычность: <...>
- Локализация: <...>
- План выхода на новые рынки: <...>

## 23. AI-Driven Automation
- AI-ассистент: <...>
- AI-инициатор: <...>
- Автоматизация: <...>

## 24. Customizable & Extensible
- Модульность: <...>
- Интеграция с внешними системами: <...>
- API-first: <...>

## 25. Visual Dashboards & Live Metrics
- Дашборды: <...>
- Live-отчёты: <...>

## 26. Knowledge Graph & Semantic Links
- Граф знаний: <...>
- AI-поиск по графу: <...>

## 27. AI-Generated Executive Summary
- Ключевые выводы: <...>
- Риски: <...>
- Возможности: <...>
- Прогнозы: <...>

## 28. Problem Space & Opportunity Mapping
- Категории проблем: <...>
- Opportunity backlog: <...>
- Пример проблем:
"""
    for i in range(1, problems_count+1):
        content += f"- Проблема {i}: <описание>\n"
    content += """

## 29. Solution Space
- User stories: <...>
- Acceptance criteria: <...>
- Альтернативы: <...>

## 30. Roadmap & Release Plan
- Gantt/story map: <...>
- Value/effort matrix: <...>

## 31. Architecture & Integrations
- Архитектура: <...>
- Интеграции: <...>
- Sequence diagrams: <...>

## 32. Analytics & Success Metrics
- KPI/OKR: <...>
- Метрики: <...>
- BI/дашборды: <...>

## 33. Security & Compliance
- Требования: <...>
- DRP: <...>

## 34. UX/UI & Accessibility
- Дизайн-система: <...>
- Accessibility: <...>

## 35. Delivery & Estimation
- Таблица: <...>
- Story points: <...>

## 36. Risks & Mitigation
- Риски: <...>
- Mitigation: <...>

## 37. Acceptance Criteria & DoD
- Критерии: <...>
- Тест-кейсы: <...>

## 38. Change Log & Decision Log
- История изменений: <...>
- Ключевые решения: <...>

## 39. Federation & Knowledge Sharing
- Экспорт/импорт: <...>

## 40. Чек-лист полноты
- [ ] ...

> AI: Все разделы автоматически проверяются на полноту, связность, актуальность. После генерации — инициировать AI-ревью, экспорт, снапшот.
"""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'projectBrief.md сгенерирован по расширенному шаблону: {out_path}')

def cmd_autofill_spec(args):
    input_path = args.input
    out_path = args.out or 'projectBrief.md'
    use_mock = getattr(args, 'mock', False)
    interactive = False

    if not input_path and not use_mock:
        print('Нет входных данных. Перехожу в интерактивный режим...')
        interactive = True

    if use_mock:
        print('Нет входных данных — генерирую тестовые данные...')
        import pandas as pd
        problems = pd.DataFrame([
            {'problem': 'High cost', 'segment': 'B2B', 'frequency': 30, 'source': 'survey'},
            {'problem': 'UX is confusing', 'segment': 'B2C', 'frequency': 25, 'source': 'feedback'},
            {'problem': 'Integration pain', 'segment': 'B2B', 'frequency': 20, 'source': 'support'},
            {'problem': 'No mobile version', 'segment': 'SMB', 'frequency': 10, 'source': 'review'},
            {'problem': 'Slow support', 'segment': 'B2C', 'frequency': 5, 'source': 'forum'},
        ])
        # Данные по конкурентам теперь опциональны
        competitors = None
        try:
            competitors = pd.DataFrame([
                {'name': 'CompA', 'segment': 'B2B', 'killer_features': 'FastAPI, Support', 'price': '$$$', 'review': 'Очень быстрый API'},
                {'name': 'CompB', 'segment': 'B2C', 'killer_features': 'UX, Mobile', 'price': '$$', 'review': 'Удобно, но дорого'},
                {'name': 'CompC', 'segment': 'SMB', 'killer_features': 'Price, Integr.', 'price': '$', 'review': 'Дёшево, мало интеграций'},
            ])
        except Exception:
            competitors = None
        data = {'problems': problems}
        if competitors is not None:
            data['competitors'] = competitors
        problems, clusters = ai_cluster_problems(problems)
        graph_md = ai_generate_graphs(clusters)
        bell_curve_md = ai_generate_bell_curve(problems)
        if competitors is not None:
            competitors_md, swot_md, unmet_md = ai_analyze_competitors(competitors)
        else:
            competitors_md = swot_md = unmet_md = ''
            print('Внимание: данные по конкурентам отсутствуют, секция будет пропущена.')
        focus_md = ai_generate_recommendations(problems, clusters)
        content = f"""
# Project Brief: <Автозаполнение — тестовые данные>

## 51. Problem Clustering & Graph Analysis
{graph_md}

## 52. Problem Distribution (Bell Curve)
{bell_curve_md}
"""
        if competitors_md or swot_md or unmet_md:
            content += f"\n## 53. Advanced Competitor Analysis\n{competitors_md}\n{swot_md}\n{unmet_md}\n"
        content += f"\n{focus_md}\n\n> AI: Для теста вы можете сгенерировать свои данные или ввести вручную. Если хотите протестировать на реальных данных — используйте опцию --input.\n"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'projectBrief.md автозаполнен тестовыми данными: {out_path}')
        return

    if interactive:
        import pandas as pd
        print('Введите 3-5 проблем (формат: проблема, сегмент, частота):')
        problems_list = []
        for i in range(3):
            p = input(f'Проблема {i+1}: ')
            s = input(f'Сегмент для проблемы {i+1}: ')
            f = input(f'Частота (число) для проблемы {i+1}: ')
            problems_list.append({'problem': p, 'segment': s, 'frequency': int(f), 'source': 'manual'})
        competitors_list = []
        add_competitors = input('Хотите добавить конкурентов? (y/n): ').strip().lower() == 'y'
        if add_competitors:
            print('Введите 2-3 конкурентов (формат: имя, сегмент, killer features, цена, отзыв):')
            for i in range(2):
                n = input(f'Имя конкурента {i+1}: ')
                s = input(f'Сегмент конкурента {i+1}: ')
                k = input(f'Killer features конкурента {i+1}: ')
                pr = input(f'Цена конкурента {i+1}: ')
                r = input(f'Отзыв о конкуренте {i+1}: ')
                competitors_list.append({'name': n, 'segment': s, 'killer_features': k, 'price': pr, 'review': r})
        problems = pd.DataFrame(problems_list)
        competitors = pd.DataFrame(competitors_list) if competitors_list else None
        data = {'problems': problems}
        if competitors is not None and not competitors.empty:
            data['competitors'] = competitors
        problems, clusters = ai_cluster_problems(problems)
        graph_md = ai_generate_graphs(clusters)
        bell_curve_md = ai_generate_bell_curve(problems)
        if competitors is not None and not competitors.empty:
            competitors_md, swot_md, unmet_md = ai_analyze_competitors(competitors)
        else:
            competitors_md = swot_md = unmet_md = ''
            print('Внимание: данные по конкурентам отсутствуют, секция будет пропущена.')
        focus_md = ai_generate_recommendations(problems, clusters)
        content = f"""
# Project Brief: <Автозаполнение — интерактивный режим>

## 51. Problem Clustering & Graph Analysis
{graph_md}

## 52. Problem Distribution (Bell Curve)
{bell_curve_md}
"""
        if competitors_md or swot_md or unmet_md:
            content += f"\n## 53. Advanced Competitor Analysis\n{competitors_md}\n{swot_md}\n{unmet_md}\n"
        content += f"\n{focus_md}\n\n> AI: Данные введены вручную. Для теста используйте --mock, для загрузки — --input.\n"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'projectBrief.md автозаполнен интерактивно: {out_path}')
        return

    # 1. Загрузка данных
    import pandas as pd
    if input_path.endswith('.csv'):
        data = pd.read_csv(input_path)
        problems = data
        competitors = None
    elif input_path.endswith('.json'):
        data = pd.read_json(input_path)
        problems = data
        competitors = None
    else:
        print('Поддерживаются только .csv и .json. Или используйте --mock для теста.')
        return
    # Попытка загрузить конкурентов, если есть соответствующий файл
    competitors_path = 'competitors_template.csv'
    if os.path.exists(competitors_path):
        competitors = pd.read_csv(competitors_path)
    else:
        competitors = None
    problems, clusters = ai_cluster_problems(problems)
    graph_md = ai_generate_graphs(clusters)
    bell_curve_md = ai_generate_bell_curve(problems)
    if competitors is not None and not competitors.empty:
        competitors_md, swot_md, unmet_md = ai_analyze_competitors(competitors)
    else:
        competitors_md = swot_md = unmet_md = ''
        print('Внимание: данные по конкурентам отсутствуют, секция будет пропущена.')
    focus_md = ai_generate_recommendations(problems, clusters)
    content = f"""
# Project Brief: <Автозаполнение>

## 51. Problem Clustering & Graph Analysis
{graph_md}

## 52. Problem Distribution (Bell Curve)
{bell_curve_md}
"""
    if competitors_md or swot_md or unmet_md:
        content += f"\n## 53. Advanced Competitor Analysis\n{competitors_md}\n{swot_md}\n{unmet_md}\n"
    content += f"\n{focus_md}\n\n> AI: Для теста вы можете сгенерировать свои данные с --mock или ввести вручную. Для реальных данных используйте --input.\n"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'projectBrief.md автозаполнен: {out_path}')

# --- Генерация шаблонов CSV ---
def cmd_generate_csv_template(args):
    import pandas as pd
    problems = pd.DataFrame([
        {'problem': 'High cost', 'segment': 'B2B', 'frequency': 30, 'source': 'survey'},
        {'problem': 'UX is confusing', 'segment': 'B2C', 'frequency': 25, 'source': 'feedback'},
    ])
    competitors = pd.DataFrame([
        {'name': 'CompA', 'segment': 'B2B', 'killer_features': 'FastAPI, Support', 'price': '$$$', 'review': 'Очень быстрый API'},
        {'name': 'CompB', 'segment': 'B2C', 'killer_features': 'UX, Mobile', 'price': '$$', 'review': 'Удобно, но дорого'},
    ])
    problems.to_csv('problems_template.csv', index=False)
    competitors.to_csv('competitors_template.csv', index=False)
    print('Сгенерированы шаблоны: problems_template.csv, competitors_template.csv')

def cmd_review_spec(args):
    file_path = args.file or 'projectBrief.md'
    out_path = args.out
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # AI-ревью: полнота, связность, дубли, рекомендации, executive summary
    checklist, recommendations, summary = ai_review_spec(content)
    review = f"""
# AI-ревью projectBrief.md

## Чек-лист полноты
{checklist}

## AI-рекомендации
{recommendations}

## Executive Summary
{summary}
"""
    print(review)
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(review)
        print(f'AI-ревью сохранено в {out_path}')

def cmd_export_spec(args):
    file_path = args.file or 'projectBrief.md'
    out_path = args.out
    fmt = args.format
    if fmt == 'pdf':
        export_to_pdf(file_path, out_path)
        print(f'Экспортировано в PDF: {out_path}')
    elif fmt == 'pptx':
        export_to_pptx(file_path, out_path)
        print(f'Презентация PPTX сгенерирована: {out_path}')
    else:
        print('Поддерживаются только форматы pdf и pptx')

def main():
    parser = argparse.ArgumentParser(description="AI-ассистент CLI: summary, links, diagram, review-changelog, roadmap, generate-spec, autofill-spec, generate-csv-template, review-spec, export-spec")
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

    p_autofill = subparsers.add_parser("autofill-spec", help="Автоматически заполнить ключевые секции projectBrief.md на основе данных")
    p_autofill.add_argument("--input", help="Путь к файлу данных (.csv/.json)")
    p_autofill.add_argument("--out", help="Путь для сохранения projectBrief.md")
    p_autofill.add_argument("--mock", action="store_true", help="Сгенерировать тестовые данные для автозаполнения")
    p_autofill.set_defaults(func=cmd_autofill_spec)

    p_generate_csv = subparsers.add_parser("generate-csv-template", help="Сгенерировать шаблоны CSV для ручного заполнения проблем и конкурентов")
    p_generate_csv.set_defaults(func=cmd_generate_csv_template)

    p_review_spec = subparsers.add_parser("review-spec", help="AI-ревью projectBrief.md: полнота, рекомендации, executive summary")
    p_review_spec.add_argument("--file", help="Путь к файлу спецификации (по умолчанию projectBrief.md)")
    p_review_spec.add_argument("--out", help="Путь для сохранения AI-ревью (например, review.md)")
    p_review_spec.set_defaults(func=cmd_review_spec)

    p_export_spec = subparsers.add_parser("export-spec", help="Экспортировать projectBrief.md/review.md в PDF или PPTX (презентацию)")
    p_export_spec.add_argument("--file", help="Путь к файлу спецификации (по умолчанию projectBrief.md)")
    p_export_spec.add_argument("--format", required=True, help="Формат экспорта: pdf или pptx")
    p_export_spec.add_argument("--out", required=True, help="Путь для сохранения (например, projectBrief.pdf или .pptx)")
    p_export_spec.set_defaults(func=cmd_export_spec)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 