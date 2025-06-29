import os
from pathlib import Path
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText

CHECKLIST_PATH = Path('memory_bank/security_audit_checklist.md')
ARCHIVE_ROOT = Path('archive')


def read_checklist():
    if not CHECKLIST_PATH.exists():
        return []
    with open(CHECKLIST_PATH, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and (line.startswith('- [') or line.startswith('* ['))]

def log_audit(audit_log_path, message):
    with open(audit_log_path, 'a', encoding='utf-8') as f:
        f.write(f'[security-audit] {message}\n')

def append_to_backlog(backlog_path, problems):
    with open(backlog_path, 'a', encoding='utf-8') as f:
        for p in problems:
            f.write(f'{p}\n')

def create_task_in_tracker(origin, problem_text):
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repo = os.environ.get('GITHUB_REPO')
    if github_token and github_repo:
        url = f'https://api.github.com/repos/{github_repo}/issues'
        headers = {'Authorization': f'token {github_token}', 'Accept': 'application/vnd.github+json'}
        data = {'title': f'[security][{origin}] {problem_text[:60]}', 'body': problem_text}
        try:
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code == 201:
                print(f'[tracker][github] Issue создано: {resp.json().get("html_url")}')
            else:
                print(f'[tracker][github] Ошибка: {resp.status_code} {resp.text}')
        except Exception as e:
            print(f'[tracker][github] Exception: {e}')
        return
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
                'summary': f'[security][{origin}] {problem_text[:60]}',
                'description': problem_text,
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
    print(f'[tracker][print] {origin}: {problem_text}')

def notify_team(origin, summary):
    msg = f'[security-audit] {origin}: {summary}'
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
            mime['Subject'] = f'Security audit for {origin}'
            mime['From'] = smtp_user
            mime['To'] = email_to
            with smtplib.SMTP_SSL(smtp_host, int(smtp_port)) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [email_to], mime.as_string())
        except Exception as e:
            print(f'[notify][email] Exception: {e}')
    else:
        print(f'[notify] {origin}: {msg}')

def run_security_audit():
    checklist = read_checklist()
    if not checklist:
        print('Чек-лист не найден, аудит пропущен.')
        return
    for origin_dir in ARCHIVE_ROOT.iterdir():
        if not origin_dir.is_dir():
            continue
        audit_log_path = origin_dir / 'auditLog.md'
        backlog_path = origin_dir / 'federation_backlog.md'
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_audit(audit_log_path, f'Запуск security audit: {now}')
        problems = [item for item in checklist if '❌' in item]
        for p in problems:
            create_task_in_tracker(origin_dir.name, p)
        if problems:
            append_to_backlog(backlog_path, problems)
            log_audit(audit_log_path, f'Найдены проблемы: {len(problems)}')
            notify_team(origin_dir.name, f'Найдены проблемы: {len(problems)}')
        else:
            log_audit(audit_log_path, 'Проблем не обнаружено.')
            notify_team(origin_dir.name, 'Проблем не обнаружено.')
        print(f'{origin_dir.name}: всего пунктов {len(checklist)}, проблем {len(problems)}')

if __name__ == '__main__':
    run_security_audit() 