import os
import argparse

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
    os.makedirs(os.path.join(path, 'memory-bank/notes'), exist_ok=True)
    for fname, content in TEMPLATES[template]:
        with open(os.path.join(path, 'memory-bank', fname), 'w') as f:
            f.write(content)
    # Создать базовое MDC-правило
    os.makedirs(os.path.join(path, '.cursor/rules'), exist_ok=True)
    with open(os.path.join(path, '.cursor/rules', 'memory-bank.mdc'), 'w') as f:
        f.write(MDC_RULE)
    print(f'Memory Bank ({template}) создан в {path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', choices=TEMPLATES.keys(), required=True)
    parser.add_argument('--project-path', default='.')
    args = parser.parse_args()
    generate_memory_bank(args.project_path, args.template) 