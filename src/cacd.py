import json
import os
from typing import Dict, Any, List
from src.mcp.memory.memory_bank import MemoryBank
import asyncio

class CACD:
    """
    CACD — обработчик команд, задач, контекста и Cursor Rules (асинхронно, PostgreSQL).
    """
    def __init__(self, dsn=None, rules_path: str = 'cursor_rules.json', tasks_path: str = 'tasks.mdf'):
        self.memory = MemoryBank(dsn)
        self.rules_path = rules_path
        self.tasks_path = tasks_path
        self.backlog: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self):
        if os.path.exists(self.rules_path):
            with open(self.rules_path, 'r') as f:
                self.rules = json.load(f)
        else:
            self.rules = []

    def _save_rules(self):
        with open(self.rules_path, 'w') as f:
            json.dump(self.rules, f, indent=2)

    def _load_tasks(self):
        if os.path.exists(self.tasks_path):
            with open(self.tasks_path, 'r') as f:
                return json.load(f)
        return []

    def _save_tasks(self, tasks):
        with open(self.tasks_path, 'w') as f:
            json.dump(tasks, f, indent=2)

    async def process_command(self, command: str, task_id: str) -> Dict[str, Any]:
        """
        Обрабатывает команду: ищет контекст, применяет правила, формирует задачу.
        """
        context = await self.memory.get_context(task_id)
        if not context:
            context = input(f'Введите контекст для задачи {task_id}: ')
            await self.memory.save_context(task_id, context)
        # Применяем правила (пример: приоритет)
        applied_rules = [r for r in self.rules if r.get('type') == 'priority']
        task = {
            'id': task_id,
            'command': command,
            'context': context,
            'rules': applied_rules,
            'status': 'pending'
        }
        # Добавляем задачу в tasks.mdf
        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)
        self.backlog.append(task)
        return task

    async def complete_task(self, task_id: str, result: str):
        """
        Завершает задачу, обновляет контекст, добавляет новое правило.
        """
        tasks = self._load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'done'
                task['result'] = result
                await self.memory.save_context(task_id, task['context'])
                # Добавляем новое правило
                new_rule = {
                    'id': f'rule{len(self.rules)+1}',
                    'type': 'priority',
                    'value': 'medium'
                }
                self.rules.append(new_rule)
                self._save_rules()
                self._save_tasks(tasks)
                self.generate_doc(task)
                break

    def generate_doc(self, task: Dict[str, Any]):
        """
        Генерирует Markdown-документацию по задаче.
        """
        os.makedirs('docs', exist_ok=True)
        doc_path = f"docs/task_{task['id']}.md"
        with open(doc_path, 'w') as f:
            f.write(f"# Task {task['id']}\n")
            f.write(f"**Command:** {task['command']}\n\n")
            f.write(f"**Context:** {task['context']}\n\n")
            f.write(f"**Rules:** {json.dumps(task['rules'], indent=2)}\n\n")
            f.write(f"**Result:** {task.get('result', '')}\n") 