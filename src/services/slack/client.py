import aiohttp
import os

async def send_message(channel: str, text: str, token: str = None):
    token = token or os.getenv('SLACK_API_TOKEN')
    if not token:
        raise ValueError('SLACK_API_TOKEN не задан')
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    payload = {'channel': channel, 'text': text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            if data.get('ok'):
                return data['ts'], data.get('message', {}).get('text', '')
            raise RuntimeError(f'Slack API error: {data}') 