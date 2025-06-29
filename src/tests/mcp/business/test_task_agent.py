import pytest
from src.mcp.agents.business.task_agent import TaskAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_task_jira():
    mock_jira = AsyncMock()
    mock_jira.create_task.return_value = {"id": "JIRA-1", "url": "https://jira/task/JIRA-1"}
    agent = TaskAgent(jira=mock_jira)
    payload = {"action": "create_task", "service": "jira", "project": "DEMO", "summary": "Test"}
    result = await agent.handle_pop(payload)
    assert result["id"] == "JIRA-1"

@pytest.mark.asyncio
async def test_create_task_linear():
    mock_linear = AsyncMock()
    mock_linear.create_task.return_value = {"id": "LIN-1", "url": "https://linear/task/LIN-1"}
    agent = TaskAgent(linear=mock_linear)
    payload = {"action": "create_task", "service": "linear", "project": "DEMO", "summary": "Test"}
    result = await agent.handle_pop(payload)
    assert result["id"] == "LIN-1"

@pytest.mark.asyncio
async def test_create_task_notion():
    mock_notion = AsyncMock()
    mock_notion.create_task.return_value = {"id": "NOTION-1", "url": "https://notion/page/NOTION-1"}
    agent = TaskAgent(notion=mock_notion)
    payload = {"action": "create_task", "service": "notion", "project": "DEMO", "summary": "Test"}
    result = await agent.handle_pop(payload)
    assert result["id"] == "NOTION-1"

@pytest.mark.asyncio
async def test_create_task_missing_fields():
    agent = TaskAgent()
    payload = {"action": "create_task", "service": "jira", "summary": "Test"}
    result = await agent.handle_pop(payload)
    assert "error" in result

@pytest.mark.asyncio
async def test_create_task_unknown_service():
    agent = TaskAgent()
    payload = {"action": "create_task", "service": "unknown", "project": "DEMO", "summary": "Test"}
    result = await agent.handle_pop(payload)
    assert result["error"].startswith("service")

@pytest.mark.asyncio
async def test_unknown_action():
    agent = TaskAgent()
    payload = {"action": "unknown"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "unknown action" 