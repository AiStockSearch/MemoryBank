from src.services.confluence.client import ConfluenceClient

class ConfluenceAgent:
    def __init__(self, client: ConfluenceClient):
        self.client = client

    async def handle_pop(self, payload: dict) -> dict:
        action = payload.get('action', 'get_page')
        if action == 'get_page':
            page_id = payload.get('page_id')
            if not page_id:
                return {"error": "page_id required"}
            page = await self.client.get_page(page_id)
            if not page:
                return {"error": "not found"}
            return page
        elif action == 'create_page':
            space_key = payload.get('space_key')
            title = payload.get('title')
            body = payload.get('body')
            if not (space_key and title and body):
                return {"error": "space_key, title, body required"}
            page = await self.client.create_page(space_key, title, body)
            if not page:
                return {"error": "create failed"}
            return page
        elif action == 'search_pages':
            cql = payload.get('cql')
            if not cql:
                return {"error": "cql required"}
            results = await self.client.search_pages(cql)
            return {"results": results}
        else:
            return {"error": "unknown action"} 