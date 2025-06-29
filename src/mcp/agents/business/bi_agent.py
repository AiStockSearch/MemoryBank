from typing import Dict
from src.services.bi.client import BIClient

class BIAgent:
    def __init__(self, client: BIClient):
        self.client = client

    async def handle_pop(self, payload: Dict) -> Dict:
        action = payload.get('action', 'send_data')
        if action == 'send_data':
            data = payload.get('data')
            if not data:
                return {"error": "data required"}
            return await self.client.send_data(data)
        elif action == 'get_report':
            metric = payload.get('metric')
            date_from = payload.get('date_from')
            date_to = payload.get('date_to')
            if not (metric and date_from and date_to):
                return {"error": "metric, date_from, date_to required"}
            report = await self.client.get_report(metric, date_from, date_to)
            return {"report": report}
        else:
            return {"error": "unknown action"} 