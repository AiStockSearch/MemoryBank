import os
import aiohttp

async def create_page(title: str, content: str, database_id: str, api_key: str = None):
    """
    Асинхронное создание страницы/таска в Notion через API.
    :param title: Заголовок страницы
    :param content: Основной текст/контент
    :param database_id: ID базы данных Notion
    :param api_key: Ключ Notion (если не указан — берётся из переменной окружения NOTION_API_KEY)
    :return: (page_id, page_url)
    Пример:
        id, url = await create_page('Test', 'Desc', 'db-xxx')
    """
    api_key = api_key or os.getenv('NOTION_API_KEY')
    if not api_key:
        raise ValueError('NOTION_API_KEY не задан')
    url = 'https://api.notion.com/v1/pages'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
    }
    payload = {
        'parent': {'database_id': database_id},
        'properties': {
            'Name': {
                'title': [{
                    'text': {'content': title}
                }]
            }
        },
        'children': [
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{
                        'type': 'text',
                        'text': {'content': content}
                    }]
                }
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            if resp.status == 200 and 'id' in data:
                page_id = data['id']
                page_url = data.get('url', f'https://www.notion.so/{page_id.replace("-","")}')
                return page_id, page_url
            raise RuntimeError(f'Notion API error: {data}') 