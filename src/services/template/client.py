import aiohttp
import os

async def create_entity(params: dict, api_key: str = None):
    """
    Асинхронное создание сущности в внешнем сервисе через API.
    :param params: dict с параметрами (например, summary, description, ...)
    :param api_key: ключ API (если не указан — берётся из переменной окружения)
    :return: (id, url)
    """
    api_key = api_key or os.getenv('TEMPLATE_API_KEY')
    if not api_key:
        raise ValueError('TEMPLATE_API_KEY не задан')
    url = 'https://api.template.com/v1/entity'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=params) as resp:
            data = await resp.json()
            if resp.status == 200 and 'id' in data:
                return data['id'], data.get('url', '')
            raise RuntimeError(f'Template API error: {data}') 