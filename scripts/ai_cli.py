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

def import_template(template_data, project_id):
    import os
    import datetime
    templates_dir = f"archive/projects/{project_id}/templates/"
    os.makedirs(templates_dir, exist_ok=True)
    filename = template_data['filename']
    source = template_data.get('source', 'external')
    origin = template_data.get('origin', '')
    version = template_data.get('version', datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    target_path = os.path.join(templates_dir, filename)
    # Если файл уже есть — не затирать, а создать версию
    if os.path.exists(target_path):
        name, ext = filename.rsplit('.', 1)
        new_name = f"{name}_{source}_{version}.{ext}"
        target_path = os.path.join(templates_dir, new_name)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(template_data['content'])
    # Сохраняем метаданные
    meta_path = target_path + '.meta.json'
    import json
    meta = {
        'source': source,
        'origin': origin,
        'version': version,
        'project_id': project_id,
        'filename': filename
    }
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'Импортирован шаблон: {target_path}')

# CLI-команда для теста импорта шаблона

def cmd_import_template(args):
    template_data = {
        'filename': args.filename,
        'content': args.content,
        'source': args.source or 'external',
        'origin': args.origin or '',
        'version': args.version or None
    }
    import_template(template_data, args.project_id)

def export_template_from_archive(args):
    import os
    import shutil
    archive_dir = f"archive/projects/{args.project_id}/templates/"
    target_dir = f"memory-bank/projects/{args.project_id}/templates/"
    os.makedirs(target_dir, exist_ok=True)
    src_path = os.path.join(archive_dir, args.filename)
    meta_path = src_path + '.meta.json'
    if not os.path.exists(src_path):
        print(f'Шаблон {args.filename} не найден в архиве.')
        return
    # Если файл уже есть — не затирать, а создать версию
    target_path = os.path.join(target_dir, args.filename)
    if os.path.exists(target_path):
        import datetime
        name, ext = args.filename.rsplit('.', 1)
        version = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{name}_restored_{version}.{ext}"
        target_path = os.path.join(target_dir, new_name)
    shutil.copy2(src_path, target_path)
    if os.path.exists(meta_path):
        shutil.copy2(meta_path, target_path + '.meta.json')
    print(f'Экспортирован шаблон из архива: {target_path}')

def batch_export_templates_from_archive(args):
    import os
    import shutil
    archive_dir = f"archive/projects/{args.project_id}/templates/"
    target_dir = f"memory-bank/projects/{args.project_id}/templates/"
    os.makedirs(target_dir, exist_ok=True)
    if not os.path.exists(archive_dir):
        print(f'В архиве нет шаблонов для проекта {args.project_id}.')
        return
    files = [f for f in os.listdir(archive_dir) if not f.endswith('.meta.json')]
    if not files:
        print(f'В архиве нет шаблонов для проекта {args.project_id}.')
        return
    for filename in files:
        src_path = os.path.join(archive_dir, filename)
        meta_path = src_path + '.meta.json'
        target_path = os.path.join(target_dir, filename)
        if os.path.exists(target_path):
            import datetime
            name, ext = filename.rsplit('.', 1)
            version = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            new_name = f"{name}_restored_{version}.{ext}"
            target_path = os.path.join(target_dir, new_name)
        shutil.copy2(src_path, target_path)
        if os.path.exists(meta_path):
            shutil.copy2(meta_path, target_path + '.meta.json')
        print(f'Экспортирован шаблон из архива: {target_path}')

def list_templates(args):
    import os
    import json
    if args.archive:
        base_dir = f"archive/projects/{args.project_id}/templates/"
    else:
        base_dir = f"memory-bank/projects/{args.project_id}/templates/"
    if not os.path.exists(base_dir):
        print(f'Нет шаблонов для проекта {args.project_id} в {"архиве" if args.archive else "рабочей папке"}.')
        return
    files = [f for f in os.listdir(base_dir) if not f.endswith('.meta.json')]
    if not files:
        print(f'Нет шаблонов для проекта {args.project_id} в {"архиве" if args.archive else "рабочей папке"}.')
        return
    print(f'Шаблоны для проекта {args.project_id} ({"архив" if args.archive else "рабочая папка"}):')
    for filename in files:
        meta_path = os.path.join(base_dir, filename + '.meta.json')
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                try:
                    meta = json.load(f)
                except Exception:
                    meta = {}
        print(f'- {filename} | source: {meta.get("source", "-")}, version: {meta.get("version", "-")}, origin: {meta.get("origin", "-")}')

def remove_template(args):
    import os
    base_dir = f"archive/projects/{args.project_id}/templates/" if args.archive else f"memory-bank/projects/{args.project_id}/templates/"
    file_path = os.path.join(base_dir, args.filename)
    meta_path = file_path + '.meta.json'
    if not os.path.exists(file_path):
        print(f'Шаблон {args.filename} не найден в {"архиве" if args.archive else "рабочей папке"}.')
        return
    confirm = input(f'Удалить шаблон {args.filename} из {"архива" if args.archive else "рабочей папки"}? (y/n): ').strip().lower()
    if confirm != 'y':
        print('Удаление отменено.')
        return
    os.remove(file_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)
    print(f'Шаблон {args.filename} удалён из {"архива" if args.archive else "рабочей папки"}.')

def federation_export_templates(args):
    import os
    import zipfile
    base_dir = f"archive/projects/{args.project_id}/templates/"
    if not os.path.exists(base_dir):
        print(f'Нет шаблонов для проекта {args.project_id} в архиве.')
        return
    files = [f for f in os.listdir(base_dir) if not f.endswith('.meta.json')]
    if not files:
        print(f'Нет шаблонов для проекта {args.project_id} в архиве.')
        return
    out_zip = args.out or f"{args.project_id}_templates.zip"
    with zipfile.ZipFile(out_zip, 'w') as zf:
        for filename in files:
            file_path = os.path.join(base_dir, filename)
            meta_path = file_path + '.meta.json'
            zf.write(file_path, arcname=filename)
            if os.path.exists(meta_path):
                zf.write(meta_path, arcname=filename + '.meta.json')
    print(f'Экспортировано в архив: {out_zip}')

def federation_import_templates(args):
    import os
    import zipfile
    import datetime
    archive_dir = f"archive/projects/{args.project_id}/templates/"
    os.makedirs(archive_dir, exist_ok=True)
    with zipfile.ZipFile(args.archive, 'r') as zf:
        for member in zf.namelist():
            target_path = os.path.join(archive_dir, member)
            # Если файл уже есть — не затирать, а создать версию
            if os.path.exists(target_path) and not member.endswith('.meta.json'):
                name, ext = member.rsplit('.', 1)
                version = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{name}_imported_{version}.{ext}"
                target_path = os.path.join(archive_dir, new_name)
            with open(target_path, 'wb') as f:
                f.write(zf.read(member))
    print(f'Импортировано шаблонов в архив проекта {args.project_id} из {args.archive}')

def audit_templates(args):
    import os
    import json
    import datetime
    base_dir = f"archive/projects/{args.project_id}/templates/" if args.archive else f"memory-bank/projects/{args.project_id}/templates/"
    if not os.path.exists(base_dir):
        print(f'Нет шаблонов для проекта {args.project_id} в {"архиве" if args.archive else "рабочей папке"}.')
        return
    files = [f for f in os.listdir(base_dir) if not f.endswith('.meta.json')]
    if not files:
        print(f'Нет шаблонов для проекта {args.project_id} в {"архиве" if args.archive else "рабочей папке"}.')
        return
    seen = {}
    dups = []
    outdated = []
    no_meta = []
    now = datetime.datetime.now()
    for filename in files:
        meta_path = os.path.join(base_dir, filename + '.meta.json')
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                try:
                    meta = json.load(f)
                except Exception:
                    meta = {}
        else:
            no_meta.append(filename)
        key = (meta.get('source', '-'), meta.get('origin', '-'), meta.get('filename', filename))
        if key in seen:
            dups.append((filename, seen[key]))
        else:
            seen[key] = filename
        # Проверка на устаревание (старше 180 дней)
        v = meta.get('version')
        if v:
            try:
                dt = datetime.datetime.strptime(v[:8], '%Y%m%d')
                if (now - dt).days > 180:
                    outdated.append(filename)
            except Exception:
                pass
    print(f'Аудит шаблонов для проекта {args.project_id} ("архив" if args.archive else "рабочая папка"):')
    if dups:
        print('Дубликаты шаблонов:')
        for f1, f2 in dups:
            print(f'  - {f1} и {f2} (одинаковый source/origin/filename)')
    else:
        print('Дубликаты не найдены.')
    if outdated:
        print('Устаревшие шаблоны (старше 180 дней):')
        for f in outdated:
            print(f'  - {f}')
    else:
        print('Устаревших шаблонов не найдено.')
    if no_meta:
        print('Шаблоны без метаданных:')
        for f in no_meta:
            print(f'  - {f}')
    else:
        print('Все шаблоны содержат метаданные.')
    print('Рекомендации:')
    if dups:
        print('- Удалите или переименуйте дубликаты.')
    if outdated:
        print('- Проверьте актуальность устаревших шаблонов.')
    if no_meta:
        print('- Добавьте метаданные к шаблонам.')
    if not (dups or outdated or no_meta):
        print('- Всё в порядке!')

def main():
    parser = argparse.ArgumentParser(description="AI-ассистент и CLI для Memory Bank")
    subparsers = parser.add_subparsers()

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

    parser_import = subparsers.add_parser('import-template', help='Импортировать шаблон в проект')
    parser_import.add_argument('--project-id', required=True, help='ID проекта')
    parser_import.add_argument('--filename', required=True, help='Имя файла шаблона')
    parser_import.add_argument('--content', required=True, help='Содержимое шаблона')
    parser_import.add_argument('--source', help='Источник шаблона')
    parser_import.add_argument('--origin', help='Оригинальный проект/ссылка')
    parser_import.add_argument('--version', help='Версия шаблона')
    parser_import.set_defaults(func=cmd_import_template)

    parser_export = subparsers.add_parser('export-template-from-archive', help='Экспортировать шаблон из архива в рабочую папку проекта')
    parser_export.add_argument('--project-id', required=True, help='ID проекта')
    parser_export.add_argument('--filename', required=True, help='Имя файла шаблона в архиве')
    parser_export.set_defaults(func=export_template_from_archive)

    parser_batch_export = subparsers.add_parser('batch-export-templates-from-archive', help='Пакетно экспортировать все шаблоны из архива в рабочую папку проекта')
    parser_batch_export.add_argument('--project-id', required=True, help='ID проекта')
    parser_batch_export.set_defaults(func=batch_export_templates_from_archive)

    parser_list = subparsers.add_parser('list-templates', help='Показать список шаблонов и их метаданных')
    parser_list.add_argument('--project-id', required=True, help='ID проекта')
    parser_list.add_argument('--archive', action='store_true', help='Искать в архиве (по умолчанию — в рабочей папке)')
    parser_list.set_defaults(func=list_templates)

    parser_remove = subparsers.add_parser('remove-template', help='Удалить шаблон из архива или рабочей папки проекта')
    parser_remove.add_argument('--project-id', required=True, help='ID проекта')
    parser_remove.add_argument('--filename', required=True, help='Имя файла шаблона')
    parser_remove.add_argument('--archive', action='store_true', help='Удалять из архива (по умолчанию — из рабочей папки)')
    parser_remove.set_defaults(func=remove_template)

    parser_fed_export = subparsers.add_parser('federation-export-templates', help='Экспортировать все шаблоны проекта в zip-архив для federation/import')
    parser_fed_export.add_argument('--project-id', required=True, help='ID проекта')
    parser_fed_export.add_argument('--out', help='Имя выходного zip-архива')
    parser_fed_export.set_defaults(func=federation_export_templates)

    parser_fed_import = subparsers.add_parser('federation-import-templates', help='Импортировать шаблоны из zip-архива в архив проекта')
    parser_fed_import.add_argument('--project-id', required=True, help='ID проекта')
    parser_fed_import.add_argument('--archive', required=True, help='Путь к zip-архиву шаблонов')
    parser_fed_import.set_defaults(func=federation_import_templates)

    parser_audit = subparsers.add_parser('audit-templates', help='Аудит шаблонов: поиск дубликатов, устаревших версий, отсутствия метаданных')
    parser_audit.add_argument('--project-id', required=True, help='ID проекта')
    parser_audit.add_argument('--archive', action='store_true', help='Проверять архив (по умолчанию — рабочая папка)')
    parser_audit.set_defaults(func=audit_templates)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 