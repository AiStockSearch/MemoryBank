import argparse
import os
import shutil
import zipfile
import sys

def export_knowledge(args):
    out = args.out or 'knowledge_export.zip'
    with zipfile.ZipFile(out, 'w') as zf:
        for folder in ['memory-bank/knowledge_packages', 'memory-bank/knowledge_packages/', 'memory-bank/']:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for f in files:
                        path = os.path.join(root, f)
                        arcname = os.path.relpath(path, '.')
                        zf.write(path, arcname)
        # Снапшоты (архивы)
        if os.path.exists('snapshots'):
            for root, _, files in os.walk('snapshots'):
                for f in files:
                    path = os.path.join(root, f)
                    arcname = os.path.relpath(path, '.')
                    zf.write(path, arcname)
    print(f'Экспортировано в {out}')

def import_knowledge(args):
    inp = args.file
    if not os.path.exists(inp):
        print(f'Файл {inp} не найден')
        sys.exit(1)
    with zipfile.ZipFile(inp, 'r') as zf:
        zf.extractall('.')
    print(f'Импортировано из {inp}')

def sync_federation(args):
    # MVP: просто копируем knowledge_export.zip между папками/инстансами
    remote = args.remote
    out = args.out or 'knowledge_export.zip'
    export_knowledge(argparse.Namespace(out=out))
    # Здесь можно добавить отправку файла по сети/ssh/scp
    print(f'Для синхронизации отправьте {out} на {remote} и выполните импорт.')

def main():
    parser = argparse.ArgumentParser(description='Federation CLI: экспорт/импорт knowledge packages, снапшотов, best practices')
    subparsers = parser.add_subparsers(dest='command')

    p_export = subparsers.add_parser('export', help='Экспортировать knowledge packages и снапшоты в zip')
    p_export.add_argument('--out', help='Путь для сохранения архива')
    p_export.set_defaults(func=export_knowledge)

    p_import = subparsers.add_parser('import', help='Импортировать knowledge packages и снапшоты из zip')
    p_import.add_argument('file', help='Путь к архиву для импорта')
    p_import.set_defaults(func=import_knowledge)

    p_sync = subparsers.add_parser('sync', help='Экспортировать и подготовить к синхронизации с другим инстансом')
    p_sync.add_argument('--remote', required=True, help='Адрес/путь другого инстанса')
    p_sync.add_argument('--out', help='Путь для сохранения архива')
    p_sync.set_defaults(func=sync_federation)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 