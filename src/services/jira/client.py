import os
import aiohttp
import base64

async def create_issue(summary: str, description: str, project_key: str, issue_type: str = 'Task', jira_url: str = None, email: str = None, api_token: str = None):
    """
    Асинхронное создание задачи в Jira Cloud через REST API.
    :param summary: Краткое описание задачи
    :param description: Описание задачи
    :param project_key: Ключ проекта (например, CUR)
    :param issue_type: Тип задачи (Task, Bug, Story...)
    :param jira_url: URL Jira (например, https://your-domain.atlassian.net)
    :param email: Email пользователя (Jira Cloud)
    :param api_token: API-токен Jira
    :return: (issue_key, issue_url)
    Пример:
        key, url = await create_issue('Test', 'Desc', 'CUR')
    """
    jira_url = jira_url or os.getenv('JIRA_URL')
    email = email or os.getenv('JIRA_EMAIL')
    api_token = api_token or os.getenv('JIRA_API_TOKEN')
    if not (jira_url and email and api_token):
        raise ValueError('JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN должны быть заданы')
    url = f'{jira_url}/rest/api/3/issue'
    auth = base64.b64encode(f'{email}:{api_token}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        'fields': {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            if resp.status == 201 and 'key' in data:
                issue_key = data['key']
                issue_url = f'{jira_url}/browse/{issue_key}'
                return issue_key, issue_url
            raise RuntimeError(f'Jira API error: {data}') 