import pytest
from src.mcp.agents.anthropic_agent import AnthropicAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_handle_pop_completion():
    mock_client = AsyncMock()
    mock_client.complete.return_value = "Ответ"
    agent = AnthropicAgent(mock_client)
    result = await agent.handle_pop({"prompt": "Привет!"})
    assert result["completion"] == "Ответ"

@pytest.mark.asyncio
async def test_handle_pop_no_prompt():
    mock_client = AsyncMock()
    agent = AnthropicAgent(mock_client)
    result = await agent.handle_pop({})
    assert result["error"] == "prompt required"

@pytest.mark.asyncio
async def test_handle_pop_no_response():
    mock_client = AsyncMock()
    mock_client.complete.return_value = None
    agent = AnthropicAgent(mock_client)
    result = await agent.handle_pop({"prompt": "Привет!"})
    assert result["error"] == "no response" 