import os
import aiohttp

async def call_openai(prompt: str, model: str = 'gpt-3.5-turbo', max_tokens: int = 512, temperature: float = 0.7, api_key: str = None) -> str:
    """
    Асинхронный вызов OpenAI Chat API (GPT-3.5/4).
    :param prompt: Текст запроса
    :param model: Модель OpenAI (gpt-3.5-turbo, gpt-4 и т.д.)
    :param max_tokens: Максимум токенов в ответе
    :param temperature: Температура выборки
    :param api_key: Ключ OpenAI (если не указан — берётся из переменной окружения OPENAI_API_KEY)
    :return: Ответ LLM (str)
    Пример:
        resp = await call_openai('Привет!', model='gpt-3.5-turbo')
    """
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError('OPENAI_API_KEY не задан')
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': temperature,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['message']['content']
            raise RuntimeError(f'OpenAI API error: {data}') 