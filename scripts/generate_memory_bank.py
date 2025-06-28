import os
import argparse
import datetime

TEMPLATES = {
    'backend': [
        ('00-project-overview.md', '# Project Overview\n\n## Name\n[Project name]\n\n## Description\n[Comprehensive description of the project, its purpose, and main goals]\n\n## Key Stakeholders\n- [List of team members, roles, and responsibilities]\n\n## Timeline and Milestones\n- [Important dates and project milestones]\n\n## Technology Stack\n- [List of languages, frameworks, libraries, and tools used]\n\n## Repository Structure\n- [Overview of main directories and their purpose]\n\n## Getting Started\n- [Setup instructions and quick start guide]\n'),
        ('01-architecture.md', '# Architecture Documentation\n\n## System Architecture\n[High-level architecture diagram or description]\n\n## Design Patterns\n- [List of design patterns used and where they\'re applied]\n\n## Data Flow\n[Description of how data flows through the system]\n\n## Security Considerations\n[Security measures and practices implemented]\n\n## Database Schema\n[Database structure and relationships]\n\n## Technical Decisions\n[Record of important technical decisions and their rationales]\n'),
        ('02-components.md', '# Components\n[Details about key components, modules, and their relationships]\n'),
        ('03-development-process.md', '# Development Process\n[Workflow, branching strategy, and deployment processes]\n'),
        ('04-api-documentation.md', '# API Documentation\n[API endpoints, parameters, and response formats]\n'),
        ('05-progress-log.md', '# Progress Log\n[Chronological record of major changes and implementations]\n'),
    ],
    'frontend': [
        ('00-project-overview.md', '# Project Overview\n[Frontend project goals, stack, and team]\n'),
        ('01-ui-structure.md', '# UI Structure\n[Component tree, state management, routing]\n'),
        ('02-components.md', '# Components\n[Reusable components, patterns, and best practices]\n'),
        ('03-development-process.md', '# Development Process\n[Workflow, code style, deployment]\n'),
        ('04-api-integration.md', '# API Integration\n[How frontend interacts with backend APIs]\n'),
        ('05-progress-log.md', '# Progress Log\n[Chronological record of major changes and implementations]\n'),
    ],
    'tasks': [
        ('business/business-tasks.md', '# Business Tasks\n\n## 1. Бизнес-цель\n- Описание: <...>\n- Value: <...>\n- Критерии успеха: <...>\n- Ответственный: <...>\n- Связанные эпики/проекты: <...>\n\n## 2. Декомпозиция по сервисам/фичам\n| Сервис/Фича | Задача | Статус | Ответственный | Ссылка на фичу |\n|-------------|--------|--------|---------------|----------------|\n| Service A   | ...    | ...    | ...           | ...            |\n'),
        ('business/epic-example.md', '# Epic: <Название эпика>\n\n## 1. Описание\n- ...\n\n## 2. Бизнес-процесс\n- ...\n\n## 3. Итоговый отчёт\n- ...\n'),
        ('business/process-example.md', '# Process: <Название процесса>\n\n## 1. Описание процесса\n- ...\n\n## 2. Влияние на бизнес\n- ...\n'),
        ('tasks/feature-example.mdf', '# Feature: <Название фичи>\n\n## 1. Описание\n- <Краткое описание фичи>\n\n## 2. Связь с бизнес-целью\n- <Ссылка на бизнесовую задачу/эпик>\n\n## 3. Что реализовано\n- <Список реализованных изменений>\n\n## 4. На что повлияло\n- <Описание влияния на продукт/бизнес-процесс>\n\n## 5. Ссылки\n- Бизнес-процесс/эпик: <ссылка>\n- Pull Request/коммит: <ссылка>\n'),
        ('tasks/implement-tasks.md', '# Implement Tasks\n\n## 1. Техническая задача\n- Описание: <...>\n- Сервис/Модуль: <...>\n- Связь с бизнес-целью: <ссылка>\n- Статус: Plan/Implement/Done\n- Ответственный: <...>\n- Дата создания: <...>\n- Дата завершения: <...>\n- Примечания: <...>\n'),
        ('tasks/creative-tasks.md', '# Creative Tasks\n\n## 1. Идея/Альтернатива\n- Описание: <...>\n- Автор/AI: <...>\n- Связанные задачи: <...>\n- Оценка (голосование/AI): <...>\n- Решение: Принято/Отклонено/В доработку\n'),
        ('tasks/reflection-tasks.md', '# Reflection / Archive\n\n## 1. Итоги реализации\n- Что удалось: <...>\n- Проблемы: <...>\n- Новые инсайты: <...>\n- Рекомендации: <...>\n- Новые задачи/планы: <...>\n'),
        ('context.md', '```mermaid\nflowchart TD\n    BZ[Бизнесовая задача<br/>(business-tasks.md)] -->|Декомпозиция| PLAN[Планирование<br/>(plan-tasks.md)]\n    PLAN -->|Если нужен креатив| CREATIVE[Креатив<br/>(creative-tasks.md)]\n    CREATIVE --> PLAN\n    PLAN -->|Готово к реализации| IMPLEMENT[Реализация<br/>(implement-tasks.md)]\n    IMPLEMENT --> REFLECT[Ретроспектива/Архив<br/>(reflection-tasks.md)]\n    REFLECT -->|Новые инсайты| PLAN\n    PLAN -->|Если не нужен креатив| IMPLEMENT\n    BZ -->|Иногда напрямую| PLAN\n```\n'),
    ]
}

MDC_RULE = '''---
description: Memory Bank implementation for persistent project knowledge
alwaysApply: true
---
# Cursor's Memory Bank
(см. https://apidog.com/blog/cline-memory-cursor/)
'''

def generate_memory_bank(path, template):
    if template == 'tasks':
        os.makedirs(os.path.join(path, 'memory-bank/business'), exist_ok=True)
        os.makedirs(os.path.join(path, 'memory-bank/tasks'), exist_ok=True)
    else:
        os.makedirs(os.path.join(path, 'memory-bank/notes'), exist_ok=True)
    for fname, content in TEMPLATES[template]:
        out_path = os.path.join(path, 'memory-bank', fname)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
            f.write(content)
    # Создать базовое MDC-правило
    os.makedirs(os.path.join(path, '.cursor/rules'), exist_ok=True)
    with open(os.path.join(path, '.cursor/rules', 'memory-bank.mdc'), 'w') as f:
        f.write(MDC_RULE)
    print(f'Memory Bank ({template}) создан в {path}')

def create_feature_file(path, feature_name, business_link=None, author=None):
    fname = f'feature-{feature_name}.mdf'
    out_path = os.path.join(path, 'memory-bank/tasks', fname)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    today = datetime.date.today().isoformat()
    content = f'''# Feature: {feature_name}

## 1. Описание
- <Краткое описание фичи>

## 2. Связь с бизнес-целью
- {business_link or '<ссылка на бизнесовую задачу/эпик>'}

## 3. Что реализовано
- <Список реализованных изменений>

## 4. На что повлияло
- <Описание влияния на продукт/бизнес-процесс>

## 5. Ссылки
- Бизнес-процесс/эпик: {business_link or '<ссылка>'}
- Pull Request/коммит: <ссылка>

---
Дата создания: {today}
Автор: {author or '<автор>'}
'''
    with open(out_path, 'w') as f:
        f.write(content)
    print(f'Feature-файл создан: {out_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', choices=TEMPLATES.keys())
    parser.add_argument('--project-path', default='.')
    parser.add_argument('--create-feature', help='Создать feature-<название>.mdf')
    parser.add_argument('--business-link', help='Ссылка на бизнесовую задачу/эпик')
    parser.add_argument('--author', help='Автор фичи')
    args = parser.parse_args()
    if args.create_feature:
        create_feature_file(args.project_path, args.create_feature, args.business_link, args.author)
    elif args.template:
        generate_memory_bank(args.project_path, args.template) 