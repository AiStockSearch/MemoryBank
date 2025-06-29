from typing import Dict
from src.services.feedback.client import FeedbackClient

class FeedbackAgent:
    def __init__(self, client: FeedbackClient):
        self.client = client

    async def handle_pop(self, payload: Dict) -> Dict:
        action = payload.get('action', 'submit_feedback')
        if action == 'submit_feedback':
            user = payload.get('user')
            text = payload.get('text')
            tags = payload.get('tags', [])
            if not user or not text:
                return {"error": "user, text required"}
            return await self.client.submit_feedback(user, text, tags)
        elif action == 'get_feedback':
            limit = payload.get('limit', 10)
            feedback = await self.client.get_feedback(limit)
            return {"feedback": feedback}
        else:
            return {"error": "unknown action"} 