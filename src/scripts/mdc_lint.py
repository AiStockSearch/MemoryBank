import sys
import os
import yaml

def validate_mdc_file(path):
    errors = []
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split('---')
    if len(parts) < 3:
        errors.append('Некорректный формат MDC (нет frontmatter)')
        return errors
    try:
        meta = yaml.safe_load(parts[1])
    except Exception as e:
        errors.append(f'Ошибка YAML: {e}')
        return errors
    if not meta.get('description') or not isinstance(meta['description'], str):
        errors.append('meta.description (str) обязателен')
    if 'alwaysApply' in meta and not isinstance(meta['alwaysApply'], bool):
        errors.append('meta.alwaysApply должен быть bool')
    if 'globs' in meta and not (isinstance(meta['globs'], str) or isinstance(meta['globs'], list)):
        errors.append('meta.globs должен быть str или list')
    return errors

def main(root):
    failed = False
    for dirpath, _, files in os.walk(root):
        for file in files:
            if file.endswith('.mdc'):
                path = os.path.join(dirpath, file)
                errs = validate_mdc_file(path)
                if errs:
                    failed = True
                    print(f'Ошибка в {path}:')
                    for err in errs:
                        print(f'  - {err}')
    if failed:
        sys.exit(1)
    print('Все MDC-правила валидны!')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.cursor/rules') 