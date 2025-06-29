from typing import Dict
from src.services.jira.client import JiraClient
from src.services.linear.client import LinearClient
from src.services.notion.client import NotionClient

class TaskAgent:
    def __init__(self, jira: JiraClient = None, linear: LinearClient = None, notion: NotionClient = None):
        self.jira = jira
        self.linear = linear
        self.notion = notion

    async def handle_pop(self, payload: Dict) -> Dict:
        action = payload.get('action', 'create_task')
        service = payload.get('service', 'jira')
        if action == 'create_task':
            summary = payload.get('summary')
            description = payload.get('description', '')
            project = payload.get('project')
            if not summary or not project:
                return {"error": "summary, project required"}
            if service == 'jira' and self.jira:
                return await self.jira.create_task(project, summary, description)
            if service == 'linear' and self.linear:
                return await self.linear.create_task(project, summary, description)
            if service == 'notion' and self.notion:
                return await self.notion.create_task(project, summary, description)
            return {"error": f"service {service} not available"}
        else:
            return {"error": "unknown action"} 