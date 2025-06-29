import pytest
from src.mcp.agents.business.feedback_agent import FeedbackAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_submit_feedback():
    mock_client = AsyncMock()
    mock_client.submit_feedback.return_value = {"status": "ok", "feedback": {"user": "user1"}}
    agent = FeedbackAgent(mock_client)
    payload = {"action": "submit_feedback", "user": "user1", "text": "Test!"}
    result = await agent.handle_pop(payload)
    assert result["status"] == "ok"
    assert result["feedback"]["user"] == "user1"

@pytest.mark.asyncio
async def test_get_feedback():
    mock_client = AsyncMock()
    mock_client.get_feedback.return_value = [{"user": "user1"}, {"user": "user2"}]
    agent = FeedbackAgent(mock_client)
    payload = {"action": "get_feedback", "limit": 2}
    result = await agent.handle_pop(payload)
    assert "feedback" in result
    assert len(result["feedback"]) == 2

@pytest.mark.asyncio
async def test_submit_feedback_missing_fields():
    mock_client = AsyncMock()
    agent = FeedbackAgent(mock_client)
    payload = {"action": "submit_feedback", "text": "Test!"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "user, text required"

@pytest.mark.asyncio
async def test_unknown_action():
    mock_client = AsyncMock()
    agent = FeedbackAgent(mock_client)
    payload = {"action": "unknown"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "unknown action" 