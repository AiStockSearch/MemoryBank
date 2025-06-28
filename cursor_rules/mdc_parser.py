import os
import yaml
from typing import Dict, Any

MDC_DELIMITER = '---'


def parse_mdc_file(filepath: str) -> Dict[str, Any]:
    """
    Парсит MDC-файл Cursor rules: frontmatter (YAML) + markdown body.
    Возвращает dict с ключами: meta (dict), body (str).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split(MDC_DELIMITER)
    if len(parts) < 3:
        raise ValueError(f"Некорректный формат MDC-файла: {filepath}")
    meta = yaml.safe_load(parts[1])
    body = MDC_DELIMITER.join(parts[2:]).strip()
    return {'meta': meta, 'body': body}


def generate_mdc_file(data: Dict[str, Any]) -> str:
    """
    Генерирует MDC-файл из dict: {'meta': dict, 'body': str}.
    Возвращает строку для записи в файл.
    """
    meta_yaml = yaml.safe_dump(data.get('meta', {}), allow_unicode=True, sort_keys=False).strip()
    body = data.get('body', '').strip()
    return f"{MDC_DELIMITER}\n{meta_yaml}\n{MDC_DELIMITER}\n{body}\n"


def validate_mdc(data: dict) -> list:
    """
    Валидация MDC-структуры. Проверяет обязательные поля и типы.
    Возвращает список ошибок (если пусто — всё ок).
    """
    errors = []
    meta = data.get('meta', {})
    body = data.get('body', '')
    # Обязательное поле description
    if not meta.get('description') or not isinstance(meta['description'], str):
        errors.append('meta.description (str) обязателен')
    # alwaysApply (bool, опционально)
    if 'alwaysApply' in meta and not isinstance(meta['alwaysApply'], bool):
        errors.append('meta.alwaysApply должен быть bool')
    # globs (str|list, опционально)
    if 'globs' in meta:
        if not (isinstance(meta['globs'], str) or isinstance(meta['globs'], list)):
            errors.append('meta.globs должен быть str или list')
    # body (str)
    if not isinstance(body, str):
        errors.append('body должен быть строкой')
    return errors 