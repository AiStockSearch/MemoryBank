from src.services.local_llm.client import LocalLLMClient

class LocalLLMAgent:
    def __init__(self, client: LocalLLMClient):
        self.client = client

    async def handle_pop(self, payload: dict) -> dict:
        prompt = payload.get('prompt')
        model = payload.get('model')
        max_tokens = payload.get('max_tokens', 1024)
        if not prompt:
            return {"error": "prompt required"}
        result = await self.client.complete(prompt, model, max_tokens)
        if not result:
            return {"error": "no response"}
        return {"completion": result} 