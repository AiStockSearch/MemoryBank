import os
import aiohttp

async def call_hf(prompt: str, model: str = 'gpt2', api_key: str = None) -> str:
    """
    Асинхронный вызов HuggingFace Inference API (text-generation).
    :param prompt: Текст запроса
    :param model: Имя модели HuggingFace (например, gpt2, bigscience/bloom)
    :param api_key: Ключ HF (если не указан — берётся из переменной окружения HF_API_KEY)
    :return: Ответ LLM (str)
    Пример:
        resp = await call_hf('Hello!', model='gpt2')
    """
    api_key = api_key or os.getenv('HF_API_KEY')
    if not api_key:
        raise ValueError('HF_API_KEY не задан')
    url = f'https://api-inference.huggingface.co/models/{model}'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {"inputs": prompt}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            # text-generation: [{'generated_text': ...}]
            if isinstance(data, list) and data and 'generated_text' in data[0]:
                return data[0]['generated_text']
            # summarization: [{'summary_text': ...}]
            if isinstance(data, list) and data and 'summary_text' in data[0]:
                return data[0]['summary_text']
            raise RuntimeError(f'HF API error: {data}') 