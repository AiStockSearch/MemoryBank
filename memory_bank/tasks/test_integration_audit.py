import pytest
from pathlib import Path
from integration_audit import create_task_in_tracker, notify_team
import os

def test_github_integration(monkeypatch):
    called = {}
    def fake_post(url, json, headers):
        called['url'] = url
        called['json'] = json
        called['headers'] = headers
        class Resp:
            status_code = 201
            def json(self):
                return {'html_url': 'https://github.com/test/issue/1'}
        return Resp()
    monkeypatch.setattr('requests.post', fake_post)
    os.environ['GITHUB_TOKEN'] = 'x'
    os.environ['GITHUB_REPO'] = 'test/repo'
    create_task_in_tracker('origin', 'Проблема для трекера')
    assert 'github' in called['url']
    del os.environ['GITHUB_TOKEN']
    del os.environ['GITHUB_REPO']

def test_jira_integration(monkeypatch):
    called = {}
    def fake_post(url, json, headers, auth):
        called['url'] = url
        called['json'] = json
        called['headers'] = headers
        called['auth'] = auth
        class Resp:
            status_code = 201
            def json(self):
                return {'key': 'JIRA-1'}
        return Resp()
    monkeypatch.setattr('requests.post', fake_post)
    os.environ['JIRA_URL'] = 'https://jira.test'
    os.environ['JIRA_USER'] = 'user'
    os.environ['JIRA_TOKEN'] = 'token'
    os.environ['JIRA_PROJECT'] = 'PRJ'
    create_task_in_tracker('origin', 'Проблема для трекера')
    assert 'jira' in called['url']
    del os.environ['JIRA_URL']
    del os.environ['JIRA_USER']
    del os.environ['JIRA_TOKEN']
    del os.environ['JIRA_PROJECT']

def test_notify_team_slack(monkeypatch):
    called = {}
    def fake_post(url, json):
        called['url'] = url
        called['json'] = json
        class Resp:
            status_code = 200
            text = ''
        return Resp()
    monkeypatch.setattr('requests.post', fake_post)
    os.environ['SLACK_WEBHOOK_URL'] = 'https://slack.test'
    notify_team('origin', 'Проблема найдена')
    assert 'slack' in called['url']
    del os.environ['SLACK_WEBHOOK_URL']

def test_notify_team_email(monkeypatch):
    sent = {}
    class FakeSMTP:
        def __init__(self, host, port):
            sent['host'] = host
            sent['port'] = port
        def login(self, user, pwd):
            sent['user'] = user
            sent['pwd'] = pwd
        def sendmail(self, from_, to, msg):
            sent['from'] = from_
            sent['to'] = to
            sent['msg'] = msg
        def __enter__(self): return self
        def __exit__(self, *a): pass
    monkeypatch.setattr('smtplib.SMTP_SSL', FakeSMTP)
    os.environ['EMAIL_TO'] = 'to@test'
    os.environ['SMTP_HOST'] = 'smtp.test'
    os.environ['SMTP_PORT'] = '465'
    os.environ['SMTP_USER'] = 'user@test'
    os.environ['SMTP_PASS'] = 'pwd'
    notify_team('origin', 'Проблема найдена')
    assert sent['host'] == 'smtp.test'
    assert sent['user'] == 'user@test'
    del os.environ['EMAIL_TO']
    del os.environ['SMTP_HOST']
    del os.environ['SMTP_PORT']
    del os.environ['SMTP_USER']
    del os.environ['SMTP_PASS']

# Для запуска: pytest memory_bank/tasks/test_integration_audit.py 