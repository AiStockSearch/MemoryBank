import argparse
import shutil
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path('archive/client-x/knowledge_packages')

TEMPLATE = '''# {name} (snapshot {date})

**Описание:**
{desc}

**Контекст:**
- Проект: {project}
- Компонент: {component}
- Причина снапшота: {reason}
- Автор: {author}
- Дата: {date}

---

## Код
```ts
{code}
```

---

## Тесты
```ts
{tests}
```

---

## Usage
```tsx
{usage}
```

---

## История изменений
- {date}: Снапшот создан ({reason})
'''

def save_snapshot(args):
    src = Path(args.file)
    if not src.exists():
        print(f'Файл {src} не найден')
        return
    code = src.read_text(encoding='utf-8')
    date = datetime.now().strftime('%Y-%m-%d')
    name = src.stem
    snapshot_name = f'{name}-snapshot-{date}.md'
    desc = args.desc or 'Без описания'
    reason = args.reason or 'Без причины'
    author = args.author or 'unknown'
    project = args.project or 'client-x'
    component = args.component or src.name
    tests = args.tests or '// ... тесты ...'
    usage = args.usage or '// ... usage ...'
    content = TEMPLATE.format(
        name=name,
        date=date,
        desc=desc,
        project=project,
        component=component,
        reason=reason,
        author=author,
        code=code,
        tests=tests,
        usage=usage
    )
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    (SNAPSHOT_DIR / snapshot_name).write_text(content, encoding='utf-8')
    print(f'Снапшот сохранён: {SNAPSHOT_DIR / snapshot_name}')

def restore_snapshot(args):
    snap = Path(args.snapshot)
    dst = Path(args.file)
    if not snap.exists():
        print(f'Снапшот {snap} не найден')
        return
    text = snap.read_text(encoding="utf-8")
    # Извлекаем код из блока ```ts ... ```
    import re
    match = re.search(r'```ts\n([\s\S]+?)```', text)
    if not match:
        print('Код не найден в снапшоте')
        return
    code = match.group(1)
    dst.write_text(code, encoding='utf-8')
    print(f'Код восстановлен в {dst}')

def main():
    parser = argparse.ArgumentParser(description='Snapshot CLI')
    subparsers = parser.add_subparsers(dest='command')

    save = subparsers.add_parser('save', help='Создать снапшот')
    save.add_argument('--file', required=True, help='Путь к файлу для снапшота')
    save.add_argument('--desc', help='Описание')
    save.add_argument('--reason', help='Причина снапшота')
    save.add_argument('--author', help='Автор')
    save.add_argument('--project', help='Проект')
    save.add_argument('--component', help='Компонент')
    save.add_argument('--tests', help='Тесты (код)')
    save.add_argument('--usage', help='Usage (код)')
    save.set_defaults(func=save_snapshot)

    restore = subparsers.add_parser('restore', help='Восстановить из снапшота')
    restore.add_argument('--snapshot', required=True, help='Путь к markdown-снапшоту')
    restore.add_argument('--file', required=True, help='Куда восстановить код')
    restore.set_defaults(func=restore_snapshot)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 