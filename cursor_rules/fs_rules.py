import os
from typing import List, Dict, Any, Optional
from .mdc_parser import parse_mdc_file, generate_mdc_file
import zipfile
import io
import subprocess

RULES_DIR = '.cursor/rules'


def list_rules(base_dir: str = RULES_DIR) -> List[Dict[str, Any]]:
    """
    Рекурсивно обходит base_dir, возвращает список правил (dict: path, meta, body).
    """
    rules = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.mdc'):
                path = os.path.join(root, file)
                try:
                    rule = parse_mdc_file(path)
                    rules.append({'path': path, 'meta': rule['meta'], 'body': rule['body']})
                except Exception as e:
                    # Можно логировать ошибку парсинга
                    continue
    return rules


def create_rule(meta: Dict[str, Any], body: str, base_dir: str = RULES_DIR, filename: Optional[str] = None, user_id: str = "system", reason: str = "", on_change=None) -> str:
    """
    Создаёт новое MDC-правило в base_dir. Возвращает путь к файлу.
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if not filename:
        # Генерируем имя файла по description или шаблону
        desc = meta.get('description', 'rule').replace(' ', '_')
        filename = f"{desc}.mdc"
    filepath = os.path.join(base_dir, filename)
    data = {'meta': meta, 'body': body}
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(generate_mdc_file(data))
    commit_rule_change(filepath, 'create', user_id, reason)
    if on_change:
        on_change('create', filepath, meta, user_id, reason)
    return filepath


def update_rule(filepath: str, meta: Dict[str, Any], body: str, user_id: str = "system", reason: str = "", on_change=None) -> None:
    """
    Обновляет существующий MDC-файл по пути filepath.
    """
    data = {'meta': meta, 'body': body}
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(generate_mdc_file(data))
    commit_rule_change(filepath, 'update', user_id, reason)
    if on_change:
        on_change('update', filepath, meta, user_id, reason)


def delete_rule(filepath: str, user_id: str = "system", reason: str = "", on_change=None) -> None:
    """
    Удаляет MDC-файл по пути filepath.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        commit_rule_change(filepath, 'delete', user_id, reason)
        if on_change:
            on_change('delete', filepath, {}, user_id, reason)


def export_rules_zip(base_dir: str = RULES_DIR) -> bytes:
    """
    Экспортирует все MDC-правила из base_dir в zip-архив (в памяти).
    Возвращает bytes zip-архива.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.mdc'):
                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, base_dir)
                    zipf.write(path, arcname)
    zip_buffer.seek(0)
    return zip_buffer.read()


def import_rules_zip(zip_bytes: bytes, base_dir: str = RULES_DIR, user_id: str = "system", reason: str = "", on_change=None) -> int:
    """
    Импортирует zip-архив с MDC-правилами в base_dir. Перезаписывает существующие.
    Возвращает количество импортированных файлов.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zipf:
        count = 0
        for name in zipf.namelist():
            if name.endswith('.mdc'):
                out_path = os.path.join(base_dir, name)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, 'wb') as f:
                    f.write(zipf.read(name))
                commit_rule_change(out_path, 'import', user_id, reason)
                if on_change:
                    # Парсим meta для webhook
                    try:
                        rule = parse_mdc_file(out_path)
                        meta = rule['meta']
                    except Exception:
                        meta = {}
                    on_change('import', out_path, meta, user_id, reason)
                count += 1
    return count


def get_rule_changelog(path: str) -> list:
    """
    Возвращает историю изменений MDC-правила (git log по файлу).
    """
    try:
        result = subprocess.run([
            "git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=iso", path
        ], capture_output=True, text=True, check=True)
        entries = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                entries.append({
                    "commit": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                })
        return entries
    except Exception as e:
        return [{"error": str(e)}]


def rollback_rule(path: str, commit: str, on_change=None) -> bool:
    """
    Откатывает MDC-правило к версии commit (git checkout <commit> -- <path>).
    """
    try:
        subprocess.run(["git", "checkout", commit, "--", path], check=True)
        commit_rule_change(path, 'rollback', reason=f'rollback to {commit}')
        if on_change:
            # Парсим meta для webhook
            try:
                rule = parse_mdc_file(path)
                meta = rule['meta']
            except Exception:
                meta = {}
            on_change('rollback', path, meta, 'system', f'rollback to {commit}')
        return True
    except Exception as e:
        print(f"Git rollback error: {e}")
        return False 