from src.services.anthropic.client import AnthropicClient

class AnthropicAgent:
    def __init__(self, client: AnthropicClient):
        self.client = client

    async def handle_pop(self, payload: dict) -> dict:
        prompt = payload.get('prompt')
        max_tokens = payload.get('max_tokens', 1024)
        if not prompt:
            return {"error": "prompt required"}
        result = await self.client.complete(prompt, max_tokens)
        if not result:
            return {"error": "no response"}
        return {"completion": result} 