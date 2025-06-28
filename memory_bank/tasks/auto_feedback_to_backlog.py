"""
Автоматическая задача: Перенос feedback в backlog

Описание:
- Скрипт мониторит новые сообщения/feedback (например, из archive/<origin>/feedback.md или внешних источников)
- Валидирует и структурирует feedback
- Добавляет новые задачи/предложения в backlog (archive/<origin>/federation_backlog.md)
- Логирует действия и ошибки
- Отправляет уведомления команде

Критерии готовности:
- Feedback автоматически появляется в backlog
- Исключены дубли
- Ведётся лог изменений
"""

# TODO: Реализовать интеграцию с источниками feedback и backlog
# TODO: Добавить логирование и уведомления

import os
from pathlib import Path
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

ARCHIVE_ROOT = Path('archive')
REPORT_PATH = ARCHIVE_ROOT / 'feedback_report.md'


def read_lines(path):
    if not path.exists():
        return set()
    with open(path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def append_lines(path, lines):
    with open(path, 'a', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

def log_audit(audit_log_path, message):
    with open(audit_log_path, 'a', encoding='utf-8') as f:
        f.write(f'[auto-feedback] {message}\n')

def is_valid_feedback(line):
    # Минимальная длина, отсутствие технических/пустых строк
    if len(line) < 10:
        return False
    if line.lower().startswith(('log:', 'debug:', 'info:', '#', '//')):
        return False
    return True

def notify_team(origin, count):
    msg = f'Origin: {origin}\nДобавлено {count} новых feedback в backlog.'
    slack_url = os.environ.get('SLACK_WEBHOOK_URL')
    email_to = os.environ.get('EMAIL_TO')
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    if slack_url:
        try:
            resp = requests.post(slack_url, json={'text': msg})
            if resp.status_code != 200:
                print(f'[notify][slack] Ошибка: {resp.text}')
        except Exception as e:
            print(f'[notify][slack] Exception: {e}')
    elif email_to and smtp_host and smtp_port and smtp_user and smtp_pass:
        try:
            mime = MIMEText(msg)
            mime['Subject'] = f'Feedback update for {origin}'
            mime['From'] = smtp_user
            mime['To'] = email_to
            with smtplib.SMTP_SSL(smtp_host, int(smtp_port)) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [email_to], mime.as_string())
        except Exception as e:
            print(f'[notify][email] Exception: {e}')
    else:
        print(f'[notify] {origin}: {msg}')

def create_task_in_tracker(origin, feedback_text):
    # GitHub Issues
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repo = os.environ.get('GITHUB_REPO')  # format: owner/repo
    if github_token and github_repo:
        url = f'https://api.github.com/repos/{github_repo}/issues'
        headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github+json'}
        data = {'title': f'[feedback][{origin}] {feedback_text[:60]}', 'body': feedback_text}
        try:
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code == 201:
                print(f'[tracker][github] Issue создано: {resp.json().get("html_url")}')
            else:
                print(f'[tracker][github] Ошибка: {resp.status_code} {resp.text}')
        except Exception as e:
            print(f'[tracker][github] Exception: {e}')
        return
    # Jira
    jira_url = os.environ.get('JIRA_URL')
    jira_user = os.environ.get('JIRA_USER')
    jira_token = os.environ.get('JIRA_TOKEN')
    jira_project = os.environ.get('JIRA_PROJECT')
    if jira_url and jira_user and jira_token and jira_project:
        api_url = f'{jira_url}/rest/api/2/issue'
        auth = (jira_user, jira_token)
        headers = {'Content-Type': 'application/json'}
        data = {
            'fields': {
                'project': {'key': jira_project},
                'summary': f'[feedback][{origin}] {feedback_text[:60]}',
                'description': feedback_text,
                'issuetype': {'name': 'Task'}
            }
        }
        try:
            resp = requests.post(api_url, json=data, headers=headers, auth=auth)
            if resp.status_code in (200, 201):
                print(f'[tracker][jira] Task создана: {resp.json().get("key")}')
            else:
                print(f'[tracker][jira] Ошибка: {resp.status_code} {resp.text}')
        except Exception as e:
            print(f'[tracker][jira] Exception: {e}')
        return
    # Fallback
    print(f'[tracker][print] {origin}: {feedback_text}')

def process_origin(origin_path):
    feedback_path = origin_path / 'feedback.md'
    backlog_path = origin_path / 'federation_backlog.md'
    audit_log_path = origin_path / 'auditLog.md'
    if not feedback_path.exists() or not backlog_path.exists():
        return {'origin': origin_path.name, 'new': 0, 'total': 0, 'valid': 0}
    feedback = read_lines(feedback_path)
    backlog = read_lines(backlog_path)
    feedback_valid = set(filter(is_valid_feedback, feedback))
    feedback_valid = set(feedback_valid)
    new_feedback = feedback_valid - backlog
    if not new_feedback:
        log_audit(audit_log_path, 'Нет новых валидных feedback для переноса.')
        return {'origin': origin_path.name, 'new': 0, 'total': len(feedback), 'valid': len(feedback_valid)}
    append_lines(backlog_path, new_feedback)
    log_audit(audit_log_path, f'Добавлено {len(new_feedback)} новых валидных feedback в backlog.')
    notify_team(origin_path.name, len(new_feedback))
    # Интеграция с таск-трекером
    for fb in new_feedback:
        create_task_in_tracker(origin_path.name, fb)
    return {'origin': origin_path.name, 'new': len(new_feedback), 'total': len(feedback), 'valid': len(feedback_valid)}

def write_report(stats):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = [f'# Feedback Activity Report\n', f'Дата: {now}\n']
    total_new = 0
    total_valid = 0
    total_all = 0
    for s in stats:
        lines.append(f"- {s['origin']}: новых — {s['new']}, валидных — {s['valid']}, всего — {s['total']}")
        total_new += s['new']
        total_valid += s['valid']
        total_all += s['total']
    lines.append(f'\n**Итого:** новых — {total_new}, валидных — {total_valid}, всего — {total_all}\n')
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

def auto_feedback_to_backlog():
    """Обходит все origin в archive/ и переносит feedback в backlog. Генерирует отчёт."""
    stats = []
    for origin_dir in ARCHIVE_ROOT.iterdir():
        if origin_dir.is_dir():
            stat = process_origin(origin_dir)
            if stat:
                stats.append(stat)
    write_report(stats)

if __name__ == '__main__':
    auto_feedback_to_backlog() 