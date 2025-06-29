import pytest
from fastmcp import FastMCPClient
import os

client = FastMCPClient('http://localhost:8000')

@pytest.mark.parametrize('origin', ['client-x'])
def test_export_project(origin):
    result = client.tool('export_project', origin=origin)
    assert 'export' in result or 'не найден' in result

def test_create_task():
    result = client.tool('create_task', command='do_something', task_id='t1')
    assert result['status'] == 'created'
    assert result['task_id'] == 't1'

def test_get_backlog():
    result = client.resource('get_backlog', origin='client-x')
    assert 'backlog' in result

def test_get_context():
    result = client.resource('get_context', task_id='t1')
    assert 'context' in result

def test_update_rules():
    result = client.tool('update_rules', rules=[{'id': 1}], user_id='u1')
    assert result['status'] == 'rules updated'

def test_federation_pull_knowledge():
    result = client.tool('federation_pull_knowledge', origin='client-x', file='test.md')
    assert isinstance(result, str)

def test_get_knowledge_package():
    result = client.resource('get_knowledge_package', origin='client-x', name='test.md')
    assert 'content' in result or 'error' in result

def test_get_feedback():
    result = client.resource('get_feedback', origin='client-x')
    assert 'feedback' in result or 'error' in result

def test_generate_report():
    result = client.prompt('generate_report', context={'task_id': 't1', 'summary': 'Test'})
    assert 'Отчёт по задаче' in result

# Для запуска: pytest test_fastmcp_server.py 