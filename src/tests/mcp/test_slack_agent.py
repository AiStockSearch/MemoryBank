import pytest
from src.mcp.agents.slack_agent import SlackAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_handle_pop_send_message():
    mock_client = AsyncMock()
    mock_client.send_message.return_value = {"ok": True, "channel": "C1", "ts": "123"}
    agent = SlackAgent(mock_client)
    result = await agent.handle_pop({"action": "send_message", "channel": "C1", "text": "hi"})
    assert result["ok"] is True
    assert result["channel"] == "C1"

@pytest.mark.asyncio
async def test_handle_pop_list_channels():
    mock_client = AsyncMock()
    mock_client.list_channels.return_value = [{"id": "C1"}, {"id": "C2"}]
    agent = SlackAgent(mock_client)
    result = await agent.handle_pop({"action": "list_channels"})
    assert "channels" in result
    assert len(result["channels"]) == 2

@pytest.mark.asyncio
async def test_handle_pop_errors():
    mock_client = AsyncMock()
    agent = SlackAgent(mock_client)
    # Нет channel/text
    result = await agent.handle_pop({"action": "send_message"})
    assert "error" in result
    # Неизвестное действие
    result = await agent.handle_pop({"action": "unknown"})
    assert result["error"] == "unknown action" 