import os
import aiohttp

async def create_issue(title: str, description: str, team_id: str, api_key: str = None):
    """
    Асинхронное создание задачи в Linear через GraphQL API.
    :param title: Заголовок задачи
    :param description: Описание задачи
    :param team_id: ID команды Linear
    :param api_key: Ключ Linear (если не указан — берётся из переменной окружения LINEAR_API_KEY)
    :return: (issue_id, issue_url)
    Пример:
        id, url = await create_issue('Test', 'Desc', 'team-xxx')
    """
    api_key = api_key or os.getenv('LINEAR_API_KEY')
    if not api_key:
        raise ValueError('LINEAR_API_KEY не задан')
    url = 'https://api.linear.app/graphql'
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json',
    }
    query = '''
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          url
        }
      }
    }
    '''
    variables = {
        'input': {
            'title': title,
            'description': description,
            'teamId': team_id,
        }
    }
    payload = {'query': query, 'variables': variables}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            issue = data.get('data', {}).get('issueCreate', {}).get('issue')
            if issue and 'id' in issue and 'url' in issue:
                return issue['id'], issue['url']
            raise RuntimeError(f'Linear API error: {data}') 