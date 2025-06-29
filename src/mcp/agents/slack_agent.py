from src.services.slack.client import SlackClient

class SlackAgent:
    def __init__(self, client: SlackClient):
        self.client = client

    async def handle_pop(self, payload: dict) -> dict:
        action = payload.get('action', 'send_message')
        if action == 'send_message':
            channel = payload.get('channel')
            text = payload.get('text')
            if not (channel and text):
                return {"error": "channel, text required"}
            resp = await self.client.send_message(channel, text)
            if not resp:
                return {"error": "send failed"}
            return resp
        elif action == 'list_channels':
            channels = await self.client.list_channels()
            return {"channels": channels}
        else:
            return {"error": "unknown action"} 