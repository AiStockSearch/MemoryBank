import pytest
from src.mcp.agents.confluence_agent import ConfluenceAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_handle_pop_get_page():
    mock_client = AsyncMock()
    mock_client.get_page.return_value = {"id": "123", "title": "Test"}
    agent = ConfluenceAgent(mock_client)
    result = await agent.handle_pop({"action": "get_page", "page_id": "123"})
    assert result["id"] == "123"
    assert result["title"] == "Test"

@pytest.mark.asyncio
async def test_handle_pop_create_page():
    mock_client = AsyncMock()
    mock_client.create_page.return_value = {"id": "456", "title": "Created"}
    agent = ConfluenceAgent(mock_client)
    result = await agent.handle_pop({"action": "create_page", "space_key": "DEV", "title": "Created", "body": "<h1>Body</h1>"})
    assert result["id"] == "456"
    assert result["title"] == "Created"

@pytest.mark.asyncio
async def test_handle_pop_search_pages():
    mock_client = AsyncMock()
    mock_client.search_pages.return_value = [{"id": "1"}, {"id": "2"}]
    agent = ConfluenceAgent(mock_client)
    result = await agent.handle_pop({"action": "search_pages", "cql": "type=page"})
    assert "results" in result
    assert len(result["results"]) == 2

@pytest.mark.asyncio
async def test_handle_pop_errors():
    mock_client = AsyncMock()
    agent = ConfluenceAgent(mock_client)
    # Нет page_id
    result = await agent.handle_pop({"action": "get_page"})
    assert "error" in result
    # Неизвестное действие
    result = await agent.handle_pop({"action": "unknown"})
    assert result["error"] == "unknown action" 