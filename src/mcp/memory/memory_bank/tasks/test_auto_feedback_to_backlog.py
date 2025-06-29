import os
import shutil
import tempfile
import pytest
from pathlib import Path
from unittest import mock

# Импортируем функции из основного скрипта
from auto_feedback_to_backlog import (
    read_lines, append_lines, is_valid_feedback, process_origin, auto_feedback_to_backlog
)

def setup_test_origin(tmp_path, feedback_lines=None, backlog_lines=None):
    origin = tmp_path / 'test-origin'
    origin.mkdir()
    (origin / 'feedback.md').write_text('\n'.join(feedback_lines or []) + '\n', encoding='utf-8')
    (origin / 'federation_backlog.md').write_text('\n'.join(backlog_lines or []) + '\n', encoding='utf-8')
    (origin / 'auditLog.md').write_text('', encoding='utf-8')
    return origin

def test_is_valid_feedback():
    assert is_valid_feedback('Полезное предложение по улучшению')
    assert not is_valid_feedback('log: debug info')
    assert not is_valid_feedback('# comment')
    assert not is_valid_feedback('short')

def test_process_origin_adds_new_feedback(tmp_path, monkeypatch):
    origin = setup_test_origin(tmp_path, feedback_lines=['Новое предложение для backlog', 'log: debug info'], backlog_lines=['Старое предложение'])
    created = []
    monkeypatch.setattr('auto_feedback_to_backlog.create_task_in_tracker', lambda o, f: created.append((o, f)))
    stat = process_origin(origin)
    backlog = read_lines(origin / 'federation_backlog.md')
    assert 'Новое предложение для backlog' in backlog
    assert stat['new'] == 1
    assert created == [('test-origin', 'Новое предложение для backlog')]

def test_process_origin_no_new_feedback(tmp_path, monkeypatch):
    origin = setup_test_origin(tmp_path, feedback_lines=['Старое предложение'], backlog_lines=['Старое предложение'])
    monkeypatch.setattr('auto_feedback_to_backlog.create_task_in_tracker', lambda o, f: None)
    stat = process_origin(origin)
    assert stat['new'] == 0

def test_auto_feedback_to_backlog_report(tmp_path, monkeypatch):
    # Подготовка двух origin
    origin1 = setup_test_origin(tmp_path, feedback_lines=['A valid feedback 1'], backlog_lines=[])
    origin2 = setup_test_origin(tmp_path, feedback_lines=['log: skip', 'Another valid feedback'], backlog_lines=['Another valid feedback'])
    # Переопределяем ARCHIVE_ROOT и REPORT_PATH
    monkeypatch.setattr('auto_feedback_to_backlog.ARCHIVE_ROOT', tmp_path)
    monkeypatch.setattr('auto_feedback_to_backlog.REPORT_PATH', tmp_path / 'feedback_report.md')
    monkeypatch.setattr('auto_feedback_to_backlog.create_task_in_tracker', lambda o, f: None)
    auto_feedback_to_backlog()
    report = (tmp_path / 'feedback_report.md').read_text(encoding='utf-8')
    assert 'test-origin' in report
    assert 'новых — 1' in report
    assert 'Another valid feedback' not in report  # не должно быть новых

# Для запуска: pytest memory_bank/tasks/test_auto_feedback_to_backlog.py 